import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Date;
import java.util.List;
import java.util.ArrayList;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.FSDirectory;

/**
 * Returns a list of string lists with the following fields:
 * username, text
 */
public class SearchAPI {
    public static void main(String[] args) throws Exception {
        BufferedReader in = new BufferedReader(new InputStreamReader(System.in));

        List<List<String>> res = search(in.readLine(), 10);

        for (List<String> row : res) {
            for (String item : row) {
                System.out.print("__ " + item);
            }
            System.out.println("");
        }

    }
    public static List<List<String>> search(String queryStr, int numResults) throws Exception {
        List<List<String>> results_list = new ArrayList<List<String>>();
        Path indexPath = Paths.get("index");
        Analyzer analyzer = new StandardAnalyzer();
        int maxHits = numResults;
        String field = "text";
        IndexReader reader = DirectoryReader.open(FSDirectory.open(indexPath));
        IndexSearcher searcher= new IndexSearcher(reader);

        QueryParser parser = new QueryParser(field, analyzer);

        Query q = parser.parse(queryStr);

        TopDocs results = searcher.search(q, 10*maxHits);
        ScoreDoc[] hits = results.scoreDocs;


        int end = Math.min(hits.length, maxHits);

        for (int i = 0; i < end; i++) {
            List<String> row = new ArrayList<String>();
            Document doc = searcher.doc(hits[i].doc);
            row.add(doc.get("user"));
            row.add(doc.get("original_text"));
            results_list.add(row);
        }
        return results_list;
    }
}