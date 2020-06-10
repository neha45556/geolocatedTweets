import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.lang.reflect.Type;
import java.util.List;
import java.util.Date;
import java.text.SimpleDateFormat;
import java.time.LocalDate;
import java.time.ZoneId;
import java.io.InputStream;
import java.nio.file.SimpleFileVisitor;
import java.nio.file.attribute.BasicFileAttributes;
import java.nio.file.FileVisitResult;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.document.LatLonPoint;
import org.apache.lucene.document.LongPoint;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.IndexWriterConfig.OpenMode;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;

import com.google.gson.reflect.TypeToken;
import com.google.gson.stream.JsonReader;
import com.google.gson.*;

public class Indexer {
    public static void main(String[] args) {
        Path indexPath = Paths.get("index");
        Path dataPath = Paths.get("data");
        if (!Files.isReadable(dataPath)) {
            System.err.printf("Error accessing data folder %s; please make sure it exists.\n", dataPath.toAbsolutePath());
            System.exit(1);
        }

        try {
            System.out.printf("Indexing to directory %s\n", indexPath.toAbsolutePath());

            Directory dir = FSDirectory.open(indexPath);
            Analyzer analyzer = new StandardAnalyzer();
            IndexWriterConfig iwc = new IndexWriterConfig(analyzer);
            iwc.setOpenMode(OpenMode.CREATE_OR_APPEND);

            IndexWriter writer = new IndexWriter(dir, iwc);
            indexEntries(writer, dataPath);
        } catch (Exception e) {
            System.out.println(e.toString());
        }
        /*
        String json = "";
        Gson gson = new Gson();
        Type tweetListType = new TypeToken<List<TweetEntry>>(){}.getType();
        List<TweetEntry> tweets = gson.fromJson(json, tweetListType);
        TweetEntry tweet = tweets.get(0);
        System.out.println(tweet.links.get(0).url); */
    }

    public static void indexEntries(IndexWriter writer, Path path) throws IOException {
        if (Files.isDirectory(path)) {
            Files.walkFileTree(path, new SimpleFileVisitor<Path>() {
                @Override
                public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) throws IOException {
                    try {
                        InputStream in = Files.newInputStream(file);
                        readJsonStream(in, writer);
                    } catch (Exception e) {
                        System.err.println(e.toString());
                    }
                    return FileVisitResult.CONTINUE;
                }
            });
        }
    }

    public static void readJsonStream(InputStream in, IndexWriter writer) throws IOException {
        JsonReader reader = new JsonReader(new InputStreamReader(in, "UTF-8"));
        Gson gson = new Gson();
        reader.beginArray();
        while (reader.hasNext()) {
            TweetEntry tweet = gson.fromJson(reader, TweetEntry.class);
            indexEntry(writer, tweet);
        }
    }

    public static void indexEntry(IndexWriter writer, TweetEntry entry) {
        Document doc = new Document();

        /**
         * Username should be searchable, but should not affect things like term frequency.
         */
        doc.add(new StringField("user", entry.user, Field.Store.YES));

        /**
         * URL Title. Should be searchable.
         */

        if (entry.links.size() > 0) {
            TweetURL urlobj = entry.links.get(0);
            if (urlobj.title != null) {
                doc.add(new StringField("link_title", urlobj.title, Field.Store.YES));
            }
        }

        /**
         * Original Tweet text.  We don't actually have a way to access the original text, so just store it in the index
         * (it's fairly small).
         */
        doc.add(new TextField("original_text", entry.text, Field.Store.YES));

        /**
         * Tweet text (analyzed).
         */
        doc.add(new TextField("text", entry.text, Field.Store.NO));

        /**
         * Coordinates.
         */
        if (entry.location != null && entry.location.coordinates.size() >= 2) {
            doc.add(new LatLonPoint("location", entry.location.coordinates.get(1), entry.location.coordinates.get(0)));
        }

        /** 
         * Date/time. e.g. 2020-06-10 21:17:51. Convert to long for easy indexing. (we only need resolution to the day)
         */
        SimpleDateFormat fmt = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        try {
            Date date = fmt.parse(entry.datetime);
            LocalDate localDate = date.toInstant().atZone(ZoneId.systemDefault()).toLocalDate();
            long month = localDate.getMonthValue();
            long year = localDate.getYear();
            long dayOfMonth = localDate.getDayOfMonth();
            long longdate = dayOfMonth + (month * 100) + (year * 100 * 100);
            doc.add(new LongPoint("date", longdate));
        } catch (Exception e) {
            // Invalid date; do nothing...
        }
    }
}