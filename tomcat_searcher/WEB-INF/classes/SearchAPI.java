import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Date;
import java.util.List;
import java.util.ArrayList;
import java.util.Calendar;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.io.*;

import javax.servlet.*;
import javax.servlet.http.*;
import javax.servlet.annotation.*;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.AtomicReaderContext;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.queries.CustomScoreQuery;
import org.apache.lucene.queries.CustomScoreProvider;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.FSDirectory;

@WebServlet("/search")
public class SearchAPI extends HttpServlet {
	class DateRelevanceQuery extends CustomScoreQuery {
		public DateRelevanceQuery(Query subQuery) {
			super(subQuery);
		}

		protected CustomScoreProvider getCustomScoreProvider(AtomicReaderContext context) throws IOException {
			return new DateRelevanceQueryScoreProvider("date", context);
	  }
	}

	class DateRelevanceQueryScoreProvider extends CustomScoreProvider {
		String _field;
		public DateRelevanceQueryScoreProvider(String field, AtomicReaderContext context) {
			super(context);
			_field = field;
		}

		public float customScore(int docIndex, float subQueryScore, float valSrcScore) throws IOException {
			float defaultScore = subQueryScore * valSrcScore;
			IndexReader reader = context.reader();
			String docDate = reader.document(docIndex).get(_field);
			if (doc == null) return defaultScore;

			int simpleDate = Integer.parseInt(docDate);
			Date currentDate = new Date();
			int year = simpleDate / (100 * 100);
			int month = (simpleDate - (year * 100 * 100)) / 100;
			int day = simpleDate - ((simpleDate / 100) * 100);
			Date docDate = new Date(year, month, day);

			long ageInDays = (currentDate.getTime() - docDate.getTime()) / 1000 / 60 / 60 / 24;
			float ageScore = (float)(Math.exp((double)(Math.max(ageInDays + 1, 1)) * -1.0));
			return ageScore * defaultScore;
    }
  }
	@Override
	public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException, ServletException{
		response.setContentType("text/html");
		PrintWriter out = response.getWriter();
		String queryStr = request.getParameter("query");
				if (queryStr == null) queryStr = new String("");
		out.println("<!DOCTYPE html>");
		out.println("<html><head>");
		out.println("<title>Tweets</title>");
		out.println("</head><body>");
		out.println("<h1>Search term</h1>");
		out.println("<form method=\"get\" action=\"/hello/search\">");
		out.println("<input type=\"text\" id=\"query\" name=\"query\" placeholder=\"purple monkey dishwasher\" autofocus><input type=\"submit\" value=\"Submit\"></form>");

				List<List<String>> results;
		if (queryStr != null && queryStr.length() != 0) {
					out.println("<p>" + queryStr + "</p>");
						try {
				results = search_index(queryStr, 20);
						} catch (Exception e) {
							results = null;
							out.println(e.toString());
						}
			out.println("<table style=\"width:100%\"><tr><th>Username</th><th>Tweet Text</th></tr>");
			for (List<String> row : results) {
				out.println("<tr>");
				for (String col : row) {
					out.println("<td>" + col + "</td>");
				}
				out.println("</tr>");
			}
			out.println("</table>");
		}
		out.println("</body></html>");
	}
	public static List<List<String>> search_index(String queryStr, int numResults) throws Exception {
		List<List<String>> results_list = new ArrayList<List<String>>();
		Path indexPath = Paths.get("index");
		Analyzer analyzer = new StandardAnalyzer();
		int maxHits = numResults;
		String field = "text";
		IndexReader reader = DirectoryReader.open(FSDirectory.open(indexPath));
		IndexSearcher searcher= new IndexSearcher(reader);

		QueryParser parser = new QueryParser(field, analyzer);

		Query q = parser.parse(queryStr);
		CustomScoreQuery cq = new DateRelevanceQuery(q);

		TopDocs results = searcher.search(cq, 10*maxHits);
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


