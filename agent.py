from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.sql import SQLTools

from agno.tools.exa import ExaTools
from agno.tools.file import FileTools  # Import FileTools for saving reports
from datetime import datetime
import json
import os

def read_file_with_fallback_encoding(file_path):
    """
    Read a file with fallback encoding options if UTF-8 fails.
    This function attempts to read files with different encodings in the following order:
    1. UTF-8
    2. cp932 (Japanese Windows encoding)
    3. shift_jis (Another Japanese encoding)
    4. latin1 (Should work for any file as a last resort)
    
    Args:
        file_path (str): Path to the file to read
        
    Returns:
        str: Contents of the file as a string
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        Exception: For other errors while reading the file
    """
    encodings = ['utf-8', 'cp932', 'shift_jis', 'latin1']
    
    # For JSON files, use binary mode first to check if it's a binary JSON file
    if file_path.lower().endswith('.json'):
        try:
            import json
            # First try to open as binary and decode with json
            with open(file_path, 'rb') as f:
                binary_data = f.read()
                # Try to load as JSON directly from binary
                return json.loads(binary_data)
        except (json.JSONDecodeError, Exception):
            # If binary JSON parsing fails, fall back to text-based approaches
            pass
            
    # Try each encoding until one works
    last_exception = None
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                return content
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except UnicodeDecodeError as e:
            # Keep track of the last exception but try the next encoding
            last_exception = e
            continue
        except Exception as e:
            last_exception = e
            break
    
    # If all encodings fail, try binary mode as a last resort
    try:
        with open(file_path, 'rb') as f:
            binary_data = f.read()
            # Try to decode as best as possible or return as string representation
            return str(binary_data)
    except Exception as e:
        last_exception = e
    
    # If everything fails, raise the last exception
    if last_exception:
        raise Exception(f"Failed to read file with any encoding: {last_exception}")

    
# OpenAI API key（実際のキーに置き換えてください）
api_key = "sk-xxxxxxxxxxx"
exa_api_key="xxxxxxxxxx"
# 今日の日付を取得（Exaの検索時に使用）
today = datetime.now().strftime("%Y-%m-%d")

# 一時ファイルのパスを定義
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(SCRIPT_DIR, "temp_files")
REPORTS_DIR = os.path.join(SCRIPT_DIR, "reports")
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
QUERY_FILE = os.path.join(TEMP_DIR, "original_query.txt")
SQL_RESULTS_FILE = os.path.join(TEMP_DIR, "sql_results.json")
WEB_RESULTS_FILE = os.path.join(TEMP_DIR, "web_results.json")
SQL_QUERY_FILE = os.path.join(TEMP_DIR, "generated_sql_query.txt")

# SQLite DBへの接続を設定
sql_tools = SQLTools(
    db_url="sqlite:///.db/it_support.db",  # SQLiteデータベースのパス
    list_tables=True,
    describe_table=True,
    run_sql_query=True
)

# ファイル操作用のツールを設定
file_tools = FileTools()

# キーワード抽出エージェント
keyword_agent = Agent(
    name="Keyword Extractor",
    model=OpenAIChat("gpt-4o-mini", api_key=api_key),
    role="""
    あなたの役割は、ITシステムの問い合わせからデータベース検索に適した重要なキーワードを抽出することです。
    
    以下のような技術的な用語を優先的に抽出してください:
    - システム名（SAP ERP、Oracle EBS、Microsoft Dynamics 365、Infor CloudSuite、Salesforceなど）
    - エラーコード（F5003、DBIF_RSQL_SQL_ERROR、V7100、ORA-01555など）
    - モジュール名（FI-GL、MM-IM、SD-SLSなど）
    - 機能名（伝票登録、外貨評価、在庫移動など）
    - カテゴリ（財務会計、販売管理、在庫管理など）
    
    出力形式:
    抽出したキーワードはカンマ区切りのリストとして返します。
    余計な説明は一切加えず、キーワードのみを返します。
    
    例:
    入力: 「SAP ERPの財務会計モジュールでFB01の伝票登録時に消費税が自動計算されません」
    出力: SAP ERP, 財務会計, FB01, 伝票登録, 消費税, 自動計算
    """,
    markdown=True,
)

# SQLクエリー提案エージェント
sql_query_agent = Agent(
    name="SQL Query Generator",
    model=OpenAIChat("gpt-4o-mini", api_key=api_key),
    role=f"""
    あなたの役割は、Keyword Extractorが出力したキーワードを使用してSQLiteデータベース向けの効果的な検索クエリーを作成することです。

    データベース構造:
    テーブル名: incidents
    主要カラム:
    - incident_number: インシデント番号
    - system_name: システム名 (SAP ERP, Oracle EBS, Microsoft Dynamics 365, Infor CloudSuite, Salesforce)
    - module: モジュール名
    - short_description: 概要
    - description: 詳細説明
    - resolution: 解決策
    - error_code: エラーコード
    - affected_version: 影響バージョン

    入力されたキーワードだけを使い、以下の条件を満たすSQLiteクエリーを生成してください:
    1. 各キーワードはLIKE演算子を使用して部分一致検索する (%keyword%)
    2. 各キーワードは複数のカラム（short_description, description, resolution,error_code）で検索する
    3. 検索結果はincident_numberの降順でソート
    4. 検索結果は最大5件に制限する

    生成されたSQLクエリーを '{SQL_QUERY_FILE}' にファイル保存してください。

    出力:
    SQLクエリーのみを返します。説明や前置きは不要です。
    """,
    tools=[file_tools],
    markdown=True,
)

# SQLクエリー実行エージェント
sql_executor_agent = Agent(
    name="SQL Query Executor",
    model=OpenAIChat("gpt-4o-mini", api_key=api_key),
    role=f"""
    あなたの役割は、SQLクエリーを使ってSQLiteデータベースに対して実行することです。
    
    実行手順:
    1. '{SQL_QUERY_FILE}'から実行するSQLを読み込んだ後、SQLToolsを使用してデータベースにクエリを実行する
    2. 検索結果の件数を表示する
    3. 取得した各レコードの完全な情報をfile_toolsを使ってローカルフォルダ内に保存する
    
    ファイル保存のルール:
    - 検索結果は必ず "{SQL_RESULTS_FILE}" に保存してください
    - JSONフォーマットで保存してください (配列形式)
    - 検索結果が0件の場合でも、空の配列として保存してください
    
    出力形式:
    1. 「検索結果: X件」の形式で件数を表示
    2. 各レコードについて以下の全ての情報を記載すること:
       - incident_number: インシデント番号
       - system_name: システム名
       - module: モジュール名
       - short_description: 概要
       - description: 詳細説明
       - resolution: 解決策
       - error_code: エラーコード
       - affected_version: 影響バージョン
    3. 結果がなかった場合は「検索結果: 0件」と表示
    4. 最後に「検索結果を {SQL_RESULTS_FILE} に保存しました」と表示
     """,
    tools=[sql_tools,file_tools],
    markdown=True,
)

# 新規Web検索エージェント
web_search_agent = Agent(
    name="Web Search Agent",
    model=OpenAIChat("gpt-4o-mini", api_key=api_key),
    role=f"""
    あなたは外部情報源から関連情報を収集し、包括的な調査報告書を作成するWeb検索エージェントです。
    データベースで情報が見つからなかった場合に、以下のツールを使いWEB検索で情報を収集します：
    
    ExaTools: より専門的かつ詳細な技術情報の検索に使用
 
    実行手順:
    1. Keyword Extractorエージェントからキーワードを受け取り、それらを使って適切な検索を実行します
    2. ExaToolsを使って情報を取得し、収集した情報を以下の構造に従った詳細なブリーフィングドキュメントにまとめます
    3. 特にエラーコードや技術的な問題の解決策に関する情報を優先します
    4. 情報源と、その情報がどのツールから取得されたかを明示します
    5. 収集した情報をfile_toolsを使って "{WEB_RESULTS_FILE}" に保存します
    
    
    ファイル保存のルール:
    - 検索結果は必ず "{WEB_RESULTS_FILE}" に保存してください
    - 検索結果が0件の場合でも、空の配列として保存してください
    
    -ファイルの出力形式:
    ```
    # [問題/技術名] に関する調査レポート

    ## 調査概要
    - **検索日時**: [現在の日時]
    - **検索方法**: ExaTools
    - **検索キーワード**: [使用したキーワード]
    - **発見件数**: X件の外部情報を発見

    ## 情報源の分析

    ### [情報源 1]
    - **URL**: [完全なURL]
    - **取得日時**: [データ取得日時]
    - **信頼性評価**: [高/中/低] - 理由: [評価理由]
    - **情報タイプ**: [公式ドキュメント/技術ブログ/フォーラム投稿/学術論文/その他]

    #### 主要内容
    [情報源から抽出した主要な内容を箇条書きで詳細に記載]
    - [重要なポイント1]
    - [重要なポイント2]
    - [重要なポイント3]

    #### 引用部分
    ```
    [情報源からの直接引用 - 特に重要な部分]
    ```

    #### 技術的詳細
    [コード例、設定例、エラーメッセージなどの技術的な詳細を構造化して記載]

    ### [情報源 2]
    [情報源1と同様の構造で記載]

    ## 解決策と推奨事項

    ### 問題の根本原因分析
    [収集した情報から導き出された問題の根本原因に関する分析]

    ### 推奨される対処方法
    1. [推奨される対処方法1 - 詳細な手順]
    2. [推奨される対処方法2 - 詳細な手順]
    3. [推奨される対処方法3 - 詳細な手順]

    ### 実装例
    ```
    [解決策の実装例（コードや設定）]
    ```

    ### 代替アプローチ
    [他の可能なアプローチとその長所・短所]

    ## 追加リソース
    - [関連する技術文書へのリンク]
    - [コミュニティフォーラムへのリンク]
    - [チュートリアルやガイドへのリンク]
    - [公式ドキュメントへのリンク]

    ## まとめ
    [調査結果の総括と最終的な推奨事項]
    ```
    
    情報が見つからない場合は、その旨を明記し、空の結果をファイルに保存してください。

    検索結果の品質向上のために以下の点を心がけてください：
    1. 情報の信頼性評価: 各情報源の信頼性を評価し、評価基準（情報源の種類、更新日時、著者の専門性など）を明示する
    2. 複数情報源からの検証: 可能な限り複数の情報源から情報を収集し、整合性を確認する
    3. 主張と事実の区別: 意見や推測と確認された事実を明確に区別する
    4. 検索キーワードの最適化: 初期結果に基づいて検索キーワードを調整し、より関連性の高い情報を収集する
    5. 時間的文脈の考慮: 情報がいつ公開されたかを考慮し、最新の情報を優先する
    6. 技術的深さ: エラーコードやログの解析、システム設定、環境要件などの技術的詳細を可能な限り収集する
    7. 解決策の実用性評価: 提案される解決策の実装の複雑さ、リソース要件、潜在的なリスクを評価する
    """,
    tools=[
        ExaTools(start_published_date=today, type="keyword", api_key=exa_api_key),
        file_tools
    ],
    markdown=True,
)

# 新規レポート作成エージェント
report_generator_agent = Agent(
    name="Report Generator",
    model=OpenAIChat("gpt-4o-mini", api_key=api_key),
    role=f"""
    あなたはIT問い合わせに対する調査結果を元に、わかりやすく構造化されたレポートを作成し、必ず reports フォルダ内に保存するエージェントです。
    
    ### 注意事項（最重要）:
    - UTF-8エンコードの問題に注意してください。日本語テキストを処理するため、すべてのテキスト操作でUTF-8エンコードを考慮する必要があります。
    - ファイル読み込みでエラーが発生した場合は、ファイルが存在するかを確認し、エラーメッセージを詳細に報告してください。
    
    ### ファイル読み込み手順:
    1. 以下のファイルから情報を読み込みます:
       - "{QUERY_FILE}" - 元の問い合わせ内容
       - "{SQL_RESULTS_FILE}" - データベース検索結果
       - "{WEB_RESULTS_FILE}" - Web検索結果（データベース検索が0件の場合のみ）
    
    2. ファイル読み込み時のエラー処理:
       - read_file_with_fallback_encoding()関数を使用してファイルを読み込みます
       - 読み込みに失敗した場合は、「ファイル読み込みエラー: [ファイル名]」と報告し、処理を続行してください
       - すべてのエラーを詳細に報告し、可能であれば代替手段を試みてください
    
    ### レポート作成の役割:
    1. 元の問い合わせ内容と検索結果（データベース、WEB検索）を元に、調査報告書を作成する
    2. 情報源を明確に記載し、回答の信頼性を担保する
    3. 問い合わせ内容、検索結果、解決策を体系的に整理する
    4. Markdownフォーマットで構造化されたレポートを作成する
    
    ### レポート作成のルール:
    1. データベース検索結果がある場合:
       - 元の問い合わせ内容と検索結果（データベース）を突き合わせて、問い合わせ内容と関係性が高い情報だけを利用して調査報告書を作成する
       - {SQL_RESULTS_FILE}から取得した全てのフィールド（incident_number, status, priority, category等）を全て漏れなく記載する
       - {SQL_RESULTS_FILE}から取得した description フィールドの内容は、いかなる場合も完全にそのまま（一言一句変えず）レポートに含めること
       - 各フィールドの値はDBから取得した正確な値をそのまま使用し、変更や要約をしない
       - 説明（description）フィールドと解決策（resolution）フィールドは特に重要であり、そのままの形で完全に記載する
       - 絶対に「...」や「省略」などで情報を短縮しない - 全ての情報を完全に表示すること
       - 「調査結果」セクションの後に「データベースレコードの詳細情報」という別セクションを設け、検索結果の全フィールドを表形式で、省略せずすべて正確に記載する
       - テキストが長い場合でも、途中で切らずに完全な形で記載すること
    
    2. Web検索結果を使用する場合:
       - ファイル保存の手順（最重要）に従い、{WEB_RESULTS_FILE}の内容をそのまま.mdファイルとして保存する。

    ### データベース検索結果のレポート構成:
    1. 概要: 問い合わせ内容と解決策の要点
    2. 問い合わせ詳細: 原文の問い合わせ内容
    4. データベースレコード{SQL_RESULTS_FILE}の詳細情報: 
       - 検索でヒットした全レコードの全フィールドを表形式で正確に表示
       - フィールド名と値を明確に対応させる
       - 長文フィールド（description, resolution）も全文を省略せずに記載
       - すべての取得可能なフィールドを含める
    5. 解決策: 
       - DBに記録された解決策を正確に引用した上で、具体的な推奨対応手順を明記する。


    ### ファイル保存の手順（最重要）:
    1. レポートが完成したら、以下の命名規則に従ったファイル名を作成する:
       - from datetime import datetime # 日付取得用にインポート
       - 現在の日付を取得: today = datetime.now().strftime("%Y%m%d")
       - 問い合わせからキーワードを抽出（例: "BenefitAccrual"）
       - ファイル名を構築: filename = f"reports/report_{today}_キーワード.md"
       - 必ず"reports/"というプレフィックスを含めること
    
    2. レポートファイルの保存:
       - file_tools.save_file(contents=レポート内容, file_name=filename, overwrite=True)
       - 保存が成功したかどうかを確認し、結果を報告する
       - 保存に失敗した場合は理由を詳細に報告し、別の方法を試みる
       - 内容がUTF-8エンコードであることを確認してからファイルを保存する
    

    """,
    tools=[file_tools, read_file_with_fallback_encoding],  # Add the new read_file_with_fallback_encoding function as a tool
    markdown=True,
)



# チームエージェントの定義（5つのエージェントを組み合わせる）
support_team = Agent(
    name="IT Support Team",
    model=OpenAIChat("gpt-4o-mini", api_key=api_key),
    team=[keyword_agent, sql_query_agent, sql_executor_agent, web_search_agent, report_generator_agent],
    instructions=[
        "ユーザーの問い合わせに対して、以下の手順でエージェントを順番に実行してください：",
        "1. Keyword Extractorを実行して重要キーワードを抽出する",
        "2. SQL Query Generatorでキーワードを基にSQLクエリを生成する",
        "3. SQL Query Executorを実行してDBを検索する",
        "4. DBで結果が0件の場合のみ、Web Search Agentを実行する",
        "5. Report Generatorを実行してレポートを作成する",
    ],
    tools=[file_tools, read_file_with_fallback_encoding],
    show_tool_calls=True,
    markdown=True,
)

# 使用例    
if __name__ == "__main__":
    # ユーザー入力を受け取る
    user_question = "給与計算バッチを実行したところ、「BenefitAccrualCalculationFailedException」というエラーメッセージが表示される"
    #user_question = "Azure環境に構築したDjangoアプリケーションで4分前後でタイムアウトが発生してしまう。"
    
    # ユーザーの問い合わせを保存（ここでクエリファイルを予め保存しておく）
    os.makedirs(os.path.dirname(QUERY_FILE), exist_ok=True)
    with open(QUERY_FILE, "w", encoding="utf-8") as f:
        f.write(user_question)
    
    # チームエージェントを実行して結果を表示
    support_team.print_response(user_question, stream=True)