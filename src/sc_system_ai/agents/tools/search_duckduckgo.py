from langchain_community.tools import DuckDuckGoSearchRun

# 検索Toolを使って、検索する
# pip install duckduckgo-search
search = DuckDuckGoSearchRun()

if __name__ == "__main__":
    input_message = "今の総理大臣は？"
    print(search.run(input_message))
