from tavily import TavilyClient

# =========================
# API KEY
# =========================

client = TavilyClient(

    api_key="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"
)

# =========================
# SEARCH FUNCTION
# =========================

def search_web(query):

    try:

        response = client.search(

            query=query,

            search_depth="basic",

            max_results=3
        )

        results = []

        for result in response["results"]:

            results.append({

                "title":
                result.get("title", ""),

                "body":
                result.get("content", "")
            })

        return results

    except Exception as e:

        print("TAVILY ERROR:", e)

        return []