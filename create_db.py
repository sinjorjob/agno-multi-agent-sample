import os
import sqlite3
import random
from datetime import datetime, timedelta
import json

def setup_database():
    """基幹系システム問い合わせ用データベースのセットアップとサンプルデータの作成"""
    # データベースディレクトリがなければ作成
    os.makedirs(".db", exist_ok=True)
    
    # SQLiteデータベースに接続
    conn = sqlite3.connect(".db/it_support.db")
    cursor = conn.cursor()
    
    # incidents テーブルの作成（既に存在する場合は削除）
    cursor.execute("DROP TABLE IF EXISTS incidents")
    cursor.execute('''
    CREATE TABLE incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_number TEXT UNIQUE,
        created_at TIMESTAMP,
        status TEXT,
        priority TEXT,
        category TEXT,
        subcategory TEXT,
        system_name TEXT,
        module TEXT,
        short_description TEXT,
        description TEXT,
        resolution TEXT,
        assigned_to TEXT,
        updated_at TIMESTAMP,
        error_code TEXT,
        affected_version TEXT
    )
    ''')
    
    # サンプルデータを生成して投入
    generate_sample_incidents(cursor, 30)
    
    # 変更をコミットして接続を閉じる
    conn.commit()
    conn.close()
    
    print("基幹系システム問い合わせデータベースのセットアップが完了しました。")


def generate_sample_incidents(cursor, count):
    """基幹系システムの具体的なインシデントチケットを生成"""
    # システム名
    systems = ["SAP ERP", "Oracle EBS", "Microsoft Dynamics 365", "Infor CloudSuite", "Salesforce"]
    
    # カテゴリとサブカテゴリとモジュールのマッピング
    categories_modules = {
        "財務会計": {
            "subcategories": ["伝票登録", "仕訳処理", "会計レポート", "期末処理", "税務計算"],
            "modules": {
                "SAP ERP": ["FI-GL", "FI-AR", "FI-AP", "FI-AA", "FI-TV"],
                "Oracle EBS": ["General Ledger", "Accounts Payable", "Accounts Receivable", "Fixed Assets"],
                "Microsoft Dynamics 365": ["Finance", "Financial Reporting", "Tax Management"],
                "Infor CloudSuite": ["General Ledger", "Receivables", "Payables"],
                "Salesforce": ["Financial Services Cloud", "Revenue Cloud"]
            }
        },
        "販売管理": {
            "subcategories": ["受注登録", "出荷処理", "請求処理", "顧客管理", "価格設定"],
            "modules": {
                "SAP ERP": ["SD-BF", "SD-MD", "SD-SLS", "SD-SHP", "SD-BIL"],
                "Oracle EBS": ["Order Management", "Shipping", "Billing"],
                "Microsoft Dynamics 365": ["Sales", "Customer Service", "Field Service"],
                "Infor CloudSuite": ["Sales Management", "Order Entry"],
                "Salesforce": ["Sales Cloud", "CPQ", "Order Management"]
            }
        },
        "在庫管理": {
            "subcategories": ["入庫処理", "出庫処理", "在庫移動", "棚卸処理", "倉庫管理"],
            "modules": {
                "SAP ERP": ["MM-IM", "MM-WM", "MM-IS", "MM-IV"],
                "Oracle EBS": ["Inventory Management", "Warehouse Management"],
                "Microsoft Dynamics 365": ["Inventory", "Warehouse Management"],
                "Infor CloudSuite": ["Inventory Control", "Warehouse Mobility"],
                "Salesforce": ["Inventory Management", "Fulfillment"]
            }
        },
        "購買管理": {
            "subcategories": ["購買依頼", "発注処理", "納品処理", "請求照合", "サプライヤー管理"],
            "modules": {
                "SAP ERP": ["MM-PUR", "MM-IV", "MM-CB"],
                "Oracle EBS": ["Purchasing", "Supplier Management"],
                "Microsoft Dynamics 365": ["Procurement", "Vendor Management"],
                "Infor CloudSuite": ["Procurement", "Strategic Sourcing"],
                "Salesforce": ["Supplier Relationship Management"]
            }
        },
        "生産管理": {
            "subcategories": ["生産計画", "製造指示", "実績記録", "工程管理", "品質管理"],
            "modules": {
                "SAP ERP": ["PP-BD", "PP-SFC", "PP-PI", "PP-PDC", "QM"],
                "Oracle EBS": ["Discrete Manufacturing", "Process Manufacturing", "Quality Management"],
                "Microsoft Dynamics 365": ["Manufacturing", "Production Control"],
                "Infor CloudSuite": ["Production Management", "Quality Management"],
                "Salesforce": ["Manufacturing Cloud"]
            }
        },
        "人事管理": {
            "subcategories": ["従業員情報", "給与計算", "勤怠管理", "人材育成", "組織管理"],
            "modules": {
                "SAP ERP": ["HCM-PA", "HCM-PY", "HCM-TM", "HCM-OM"],
                "Oracle EBS": ["Human Resources", "Payroll", "Time & Labor"],
                "Microsoft Dynamics 365": ["Human Resources", "Talent"],
                "Infor CloudSuite": ["Human Capital Management", "Talent Management"],
                "Salesforce": ["Work.com", "Employee Experience"]
            }
        },
        "システム管理": {
            "subcategories": ["権限設定", "マスタデータ", "バッチ処理", "インターフェース", "システム設定"],
            "modules": {
                "SAP ERP": ["BC-SEC", "BC-XDC", "BC-BMT", "BC-SRV"],
                "Oracle EBS": ["System Administration", "Applications DBA"],
                "Microsoft Dynamics 365": ["System Administration", "Platform"],
                "Infor CloudSuite": ["Security Management", "Data Management"],
                "Salesforce": ["Administration", "Platform Services"]
            }
        }
    }
    
    # ステータスのリスト
    statuses = ["新規", "進行中", "解決済み", "クローズ"]
    
    # 優先度のリスト
    priorities = ["高", "中", "低"]
    
    # 担当者のリスト（専門性を反映）
    assignees = {
        "財務会計": ["鈴木会計スペシャリスト", "高橋財務担当", "佐藤SAP FIコンサルタント"],
        "販売管理": ["山田販売管理", "田中SD担当", "伊藤CRMスペシャリスト"],
        "在庫管理": ["中村在庫管理", "小林倉庫管理者", "加藤MMスペシャリスト"],
        "購買管理": ["渡辺購買担当", "松本調達スペシャリスト", "井上SRMコンサルタント"],
        "生産管理": ["木村生産管理", "林製造担当", "清水PPスペシャリスト"],
        "人事管理": ["山本人事システム", "中島給与担当", "岡田HCMコンサルタント"],
        "システム管理": ["斎藤システム管理者", "近藤BASISコンサルタント", "遠藤インフラ担当"]
    }
    
    # 影響を受けるバージョン
    versions = {
        "SAP ERP": ["ECC 6.0", "S/4HANA 1909", "S/4HANA 2020", "S/4HANA 2021", "S/4HANA Cloud"],
        "Oracle EBS": ["R12.1.3", "R12.2.4", "R12.2.9", "R12.2.10", "Cloud ERP"],
        "Microsoft Dynamics 365": ["2019 Release Wave 2", "2020 Release Wave 1", "2020 Release Wave 2", "2021 Release Wave 1"],
        "Infor CloudSuite": ["v11.0.1", "v11.0.2", "v11.1.0", "v11.2.0"],
        "Salesforce": ["Winter '21", "Spring '21", "Summer '21", "Winter '22"]
    }
    
    # 現在日時を基準に過去30日分のデータを生成
    now = datetime.now()
    
    # 具体的な基幹系システムのインシデントテンプレート
    incidents_data = [
        # SAP ERP - 財務会計 - 伝票登録
        {
            "system_name": "SAP ERP",
            "category": "財務会計",
            "subcategory": "伝票登録",
            "module": "FI-GL",
            "short_description": "FB01で伝票登録時に消費税計算が正しく行われない",
            "description": "取引先からの請求書を伝票登録する際、FB01で消費税計算が正しく行われません。税コードVSTを選択しているにもかかわらず、消費税が自動計算されません。入力手順は以下の通りです：\n1. FB01でトランザクションを開始\n2. 会社コード1000、伝票タイプKRを入力\n3. 基準日と転記日は当月20日\n4. 仕入先コード10000、借方科目40000を入力\n5. 金額100,000円、税コードVSTを選択\n期待される結果は消費税10,000円が自動計算されることですが、0円と表示されます。システムバージョンはS/4HANA 1909です。",
            "resolution": "SAP S/4HANA 1909 SP02で発生している既知の問題を確認しました。取引先マスタの税分類が正しく設定されていないことが原因でした。以下の手順で解決しました：\n1. トランザクションXK02で取引先マスタを表示\n2. 「会社コードデータ」タブを選択\n3. 「税分類」で「課税」を選択し保存\n4. SAPサポートノート2876432を参照し、標準設定を確認\nこれにより税計算が正しく機能するようになりました。また、同様の問題が発生しないよう、全取引先マスタの税設定状況を確認し、一括で修正するALVレポートプログラムを開発して提供しました。",
            "error_code": "F5003",
            "affected_version": "S/4HANA 1909"
        },
        # SAP ERP - 財務会計 - 仕訳処理
        {
            "system_name": "SAP ERP",
            "category": "財務会計",
            "subcategory": "仕訳処理",
            "module": "FI-GL",
            "short_description": "FAGL_FC_VALUATIONで外貨評価実行時にダンプが発生",
            "description": "月末の決算処理で外貨評価プログラム（FAGL_FC_VALUATION）を実行したところ、DBIF_RSQL_SQL_ERRORというダンプが発生しました。選択条件は以下の通りです：\n- 会社コード：1000\n- 評価キー：0001（標準為替差額評価）\n- 評価日：2023/04/30\n- 通貨：USD、EUR、GBP\n特に外貨建て売掛金の評価で問題が発生しています。前月は正常に処理できていました。",
            "resolution": "データベーステーブルFAGLFLEXA内の外貨残高レコードに不整合があることを確認しました。以下の手順で解決しました：\n1. FAGL_FC_VALUATION実行時のダンプログを分析し、SQL文のエラー箇所を特定\n2. トランザクションSM13で外貨残高更新の不完全な更新（Status 'A'）がないか確認\n3. 報告トランザクションFAGLF03で不整合のある外貨元帳勘定を特定（科目11000のUSD残高）\n4. トランザクションFAGL_FC_UPDATEを使用して外貨残高テーブルを修復\n5. SAP注意事項3184762を適用\nこれにより外貨評価プログラムが正常に実行できるようになりました。また、再発防止のため、月次で外貨残高整合性チェックを実施するよう運用手順を変更しました。",
            "error_code": "DBIF_RSQL_SQL_ERROR",
            "affected_version": "S/4HANA 2020"
        },
        # SAP ERP - 販売管理 - 受注登録
        {
            "system_name": "SAP ERP",
            "category": "販売管理",
            "subcategory": "受注登録",
            "module": "SD-SLS",
            "short_description": "VA01で注文を作成すると「価格設定で材料XYZに対して条件が見つかりません」というエラー",
            "description": "新規受注登録トランザクションVA01で以下の手順で注文を登録しています：\n1. 受注タイプORを選択\n2. 販売組織1000、流通チャネル10、事業部00を入力\n3. 得意先番号2000100を入力\n4. 材料番号100-200を入力、数量5個\n以上の入力後、「価格設定で材料100-200に対して条件が見つかりません」というエラーが発生し、受注登録が完了できません。この材料は先週まで問題なく注文できており、マスタデータは変更されていません。",
            "resolution": "条件レコードの有効期限切れが原因でした。以下の対応を実施して解決しました：\n1. トランザクションVK11で該当材料の価格条件を確認\n2. 標準価格（条件タイプPR00）の有効期限が先週末で終了していたことを確認\n3. トランザクションVK11で新規条件レコードを作成：\n   - 材料100-200に対して\n   - 条件タイプPR00（標準価格）\n   - 金額10,000円\n   - 有効期間：本日から12か月間\n4. 権限上の理由から本来営業部門が実施すべき処理であることを確認し、価格管理プロセスを見直し\n5. 条件レコード有効期限の一括監視レポートを営業管理部門に提供\nこれにより受注登録が正常に行えるようになりました。また、価格条件の管理ルールを整備し、期限切れの3週間前にアラートが届くよう仕組みを構築しました。",
            "error_code": "V7100",
            "affected_version": "ECC 6.0"
        },
        # SAP ERP - 在庫管理 - 在庫移動
        {
            "system_name": "SAP ERP",
            "category": "在庫管理",
            "subcategory": "在庫移動",
            "module": "MM-IM",
            "short_description": "工場間の在庫移動（MIGO）でバッチ管理材料の入庫ができない",
            "description": "トランザクションMIGOを使用して工場間の在庫移動（移動タイプ301）を行う際、バッチ管理している材料のみ入庫処理ができません。具体的な手順は以下の通りです：\n1. MIGOで「入庫」→「移動伝票で」を選択\n2. 移動タイプ301、工場1000から工場2000への移動\n3. 材料番号RAW-500（バッチ管理あり）を入力し、数量100kgを入力\n4. バッチ番号B2023001を指定\n5. 「転記」ボタンをクリック\nするとエラーメッセージ「バッチB2023001に対するバッチシリアル番号が存在しません」が表示されます。バッチ管理していない材料は問題なく移動できます。",
            "resolution": "この問題は工場2000でバッチ管理プロファイルの設定が不適切だったことが原因でした。解決手順は以下の通り：\n1. トランザクションMMC1で材料RAW-500のバッチ管理設定を確認\n2. 工場2000に対するバッチレベルが「工場レベル+材料レベル」に設定されていたが、移動元の工場1000は「材料レベルのみ」だった\n3. トランザクションSPRO→「ロジスティクス - 一般」→「バッチ管理」→「バッチ検索戦略の定義」で設定を確認\n4. 内部移動用のバッチ決定カスタマイズを修正し、工場間でバッチ定義の互換性を確保\n5. バッチ制限なしで移動できるよう、一時的に代替移動タイプ309を使用する手順を提供\n恒久対策として、全工場でのバッチ管理設定を統一し、設定変更の影響評価プロセスを強化しました。",
            "error_code": "M7931",
            "affected_version": "S/4HANA 2020"
        },
        # SAP ERP - 購買管理 - 発注処理
        {
            "system_name": "SAP ERP",
            "category": "購買管理",
            "subcategory": "発注処理",
            "module": "MM-PUR",
            "short_description": "ME21Nで発注書を作成すると、承認ワークフローが開始されない",
            "description": "トランザクションME21Nで新規の発注書を作成した後、通常は承認ワークフローが自動的に開始されるはずですが、現在ワークフローが開始されない状況が発生しています。具体的な手順は：\n1. ME21Nで発注書を作成（文書タイプNB、購買組織1000）\n2. 取引先、納期、材料、価格などを入力\n3. 発注金額は50万円（承認必要金額）\n4. 保存すると発注書番号は採番されるが、承認ワークフローが開始されない\n5. トランザクションSWI1で確認すると、該当の発注書に対するワークアイテムが存在していない\n他のユーザーも同様の症状が出ており、承認者がいないため発注書を送信できない状況です。先週まではこの問題は発生していませんでした。",
            "resolution": "先週実施されたSAPシステムアップグレード後のワークフロー設定が正しく有効化されていないことが原因でした。以下の手順で解決しました：\n1. トランザクションSWU3でワークフローのデバッグログを有効化\n2. テスト発注を作成し、ログを分析\n3. ワークフローイベントリンケージに問題があることを発見（イベントPURCHASE_ORDER_CREATEDとワークフローテンプレートWS20000054のリンクが無効化されていた）\n4. トランザクションSWEで該当イベントとワークフローのリンケージを再設定\n5. SAPサポートノート2847356を適用\n6. トランザクションSWU0でワークフローランタイム設定をリフレッシュ\nこれにより承認ワークフローが正常に動作するようになりました。また、今後のアップグレード後には自動的にワークフロー設定の検証を行うチェックリストを追加しました。",
            "error_code": "WF839",
            "affected_version": "S/4HANA 2021"
        },
        # Oracle EBS - 財務会計 - 期末処理
        {
            "system_name": "Oracle EBS",
            "category": "財務会計",
            "subcategory": "期末処理",
            "module": "General Ledger",
            "short_description": "期間終了処理実行時に「ORA-01555: snapshot too old」エラーが発生",
            "description": "Oracle EBSの一般会計モジュールで5月の期間終了処理を実行しようとしたところ、「ORA-01555: snapshot too old」エラーが発生し、処理が完了しません。具体的な操作手順：\n1. 責任：GL管理者\n2. ナビゲーション：期間 > 期間終了 > 開放/終了\n3. 期間：2023年5月、会計カレンダー：標準\n4. 「終了」ボタンをクリック\n処理が約20分実行された後にエラーが発生します。4月までの期間終了処理は問題なく実行できていました。",
            "resolution": "データベースの UNDO 領域設定が不十分であることが原因でした。大量データを処理する期間終了処理中に、トランザクションの長時間実行によりスナップショットが期限切れになっていました。解決手順：\n1. DBAチームと協力し、Oracle Enterprise Managerでトランザクションの実行状況を分析\n2. UNDO_RETENTION パラメータの値が不足していることを確認（現在値：10800秒）\n3. UNDO_RETENTION パラメータを 21600秒（6時間）に増加\n4. UNDO表領域のサイズを 5GB から 10GB に拡張\n5. GL_INTERFACE テーブルに多数の未処理トランザクションが蓄積されていることを発見し、これらを適切にインポート処理\n6. GL期間終了プロセスを複数のより小さなサブタスクに分割して実行する手順を文書化\nこれにより期間終了処理が正常に完了するようになりました。さらに、期間終了処理前のチェックリストを作成し、未処理データの事前クリーンアップを標準手順に組み込みました。",
            "error_code": "ORA-01555",
            "affected_version": "R12.2.9"
        },
        # Oracle EBS - 販売管理 - 請求処理
        {
            "system_name": "Oracle EBS",
            "category": "販売管理",
            "subcategory": "請求処理",
            "module": "Billing",
            "short_description": "自動請求実行プログラム（AutoInvoice）が一部の受注明細を処理しない",
            "description": "夜間バッチで実行されるAutoInvoiceプログラムが、特定の受注明細行を請求書に変換せず処理対象外としています。問題の詳細：\n1. 受注番号SO-123456の明細行（回線工事）が請求書に変換されていない\n2. AutoInvoiceのログで「Missing Accounting Flexfield segments.」というエラーメッセージを確認\n3. 受注ステータスは「出荷完了」になっている\n4. 受注入力画面のワークフローステータスは「承認済み」\n5. RA_INTERFACE_LINES_ALLテーブルには該当データが正しく登録されている\n同様の製品・サービスを含む他の受注明細は正常に請求書化されています。顧客への請求が遅延しており早急な解決が必要です。",
            "resolution": "この問題は、特定の品目カテゴリ（回線工事サービス）に対する売上アカウントの自動割当ルールが不適切に設定されていたことが原因でした。解決手順：\n1. AR > 設定 > トランザクション > AutoInvoice > 検証 メニューから検証レポートを実行し、詳細エラーを確認\n2. 「回線工事」品目カテゴリに対する勘定科目セグメント値の一部（利益センターセグメント）が未定義\n3. AR > 設定 > トランザクション > AutoInvoice > 勘定科目作成ワークシート で該当品目カテゴリの設定を確認\n4. 欠落していた利益センターセグメント値「1350」を配布ルールに追加\n5. Oracle Support ドキュメント ID 2155142.1 を参照し、設定を検証\n6. RA_INTERFACE_LINESのSTATUSを「WAITING」に更新し、AutoInvoiceを再実行\nこれにより該当の受注明細が正常に請求書化されました。また、品目カテゴリ設定変更時の検証プロセスを改善し、勘定科目配布ルールを定期的に検証する手順を導入しました。",
            "error_code": "ONT-2033",
            "affected_version": "R12.2.10"
        },
        # Microsoft Dynamics 365 - 人事管理 - 給与計算
        {
            "system_name": "Microsoft Dynamics 365",
            "category": "人事管理",
            "subcategory": "給与計算",
            "module": "Human Resources",
            "short_description": "給与計算処理で「福利厚生費の累計計算エラー」が発生",
            "description": "6月の給与計算バッチを実行したところ、「BenefitAccrualCalculationFailedException: Failed to calculate benefit balance for employee 000352」というエラーメッセージが表示され、処理が中断されました。問題の詳細：\n1. 人事 > 定期処理 > 給与計算 から給与計算バッチを実行\n2. 処理開始後約10分でエラーが発生し、従業員ID 000352の処理で停止\n3. 給与計算ログファイルに福利厚生費の累計計算に関するエラーが記録されている\n4. 該当従業員の福利厚生プランは「標準健康保険プラン」と「選択型退職金プラン」\n5. 5月までの給与計算は正常に処理されていた\n6. 先月該当従業員の雇用形態が変更された（契約社員から正社員へ）\n給与締め日が迫っており、早急な解決が必要です。",
            "resolution": "この問題は雇用形態変更時の福利厚生プラン移行処理が不完全だったことが原因です。以下の手順で解決しました：\n1. PowerShell診断ツールを使用して詳細なエラーログを取得・分析\n2. 従業員ID 000352の福利厚生登録データを確認し、雇用形態変更前の契約社員用プラン情報が残存していることを発見\n3. 人事 > 従業員 > 福利厚生 で該当従業員の重複登録を確認\n4. バックエンドデータベース上のHcmEmployeeBenefitテーブルで終了日が設定されていない旧プランレコードを特定\n5. Microsoft Dynamics Support Article KB4598232を参照し、正しい修正手順を確認\n6. 福利厚生管理画面から旧プランの終了処理を適切に実施（終了日を雇用形態変更日に設定）\n7. システム管理者権限でBenefit Calculation Cacheをリセット\n8. 給与計算バッチを再実行\nこれにより給与計算が正常に完了しました。また、雇用形態変更手順書を更新し、福利厚生プラン移行の正しい手続きを明確化しました。",
            "error_code": "BenefitAccrualCalculationFailedException",
            "affected_version": "2020 Release Wave 2"
        },
        # Infor CloudSuite - システム管理 - インターフェース
        {
            "system_name": "Infor CloudSuite",
            "category": "システム管理",
            "subcategory": "インターフェース",
            "module": "Data Management",
            "short_description": "基幹システムからのマスタデータ連携が失敗する",
            "description": "SAPシステムからInfor CloudSuiteへの夜間マスタデータ連携が失敗しています。具体的な状況：\n1. 毎晩23:00に実行されるION統合フローで、SAPからInforへ取引先マスタデータを同期\n2. IONデスクで確認すると、ドキュメントステータスが「エラー」になっている\n3. エラーメッセージ：「Field 'TaxID' validation failed. Value does not match pattern.」\n4. 失敗したドキュメント数：約50件（新規追加された取引先）\n5. エラー発生は昨日（5月15日）から\n6. SAP側システムの変更：先週末に国際対応のためのシステム改修を実施\nこの問題により、新規取引先との取引処理が遅延しています。",
            "resolution": "この問題は、SAP側のシステム改修で取引先マスタの税ID形式が変更されたことが原因でした。解決手順：\n1. ION Desk > Document Flow > Failed Documents から失敗ドキュメントを詳細分析\n2. エラーとなっている取引先の税IDが新形式（国コード付き形式：JP1234567890）に変更されていることを確認\n3. Infor側のデータ検証ルールは旧形式（国コードなし：1234567890）を想定していた\n4. ION Connect > Data Type Definition で取引先マスタのTaxIDフィールド定義を確認\n5. 検証パターンを「^[0-9]{10}$」から「^[A-Z]{2}[0-9]{10}$|^[0-9]{10}$」に変更し、両形式を許容\n6. ION API Gatewayのキャッシュをリフレッシュ\n7. ION Desk > Document Flow > Failed Documents から該当ドキュメントを再処理\nこれによりマスタデータ連携が正常に完了しました。さらに、システム間連携の変更影響分析プロセスを改善し、SAP側の変更が発生する場合は事前にInfor側のデータ検証ルールを確認する手順を追加しました。",
            "error_code": "ION-VAL-1022",
            "affected_version": "v11.0.2"
        },
        # SalesForce - 販売管理 - 価格設定
        {
            "system_name": "Salesforce",
            "category": "販売管理",
            "subcategory": "価格設定",
            "module": "CPQ",
            "short_description": "複数商品の見積書作成時に「FIELD_CUSTOM_VALIDATION_EXCEPTION」エラーが発生",
            "description": "Salesforce CPQで複数商品を含む見積書を作成しようとした際に、「FIELD_CUSTOM_VALIDATION_EXCEPTION: 割引率が承認範囲を超えています」というエラーが発生します。具体的な手順：\n1. 商談「OPP-2023-1234」から新規見積書を作成\n2. 製品「エンタープライズライセンス」（単価100万円）を追加\n3. 数量を10に設定\n4. 特別割引率を15%に設定\n5. 製品「メンテナンスサービス」（単価20万円）を追加\n6. 数量を10に設定\n7. 特別割引率を10%に設定\n8. 「保存」ボタンをクリック\nこの時点でバリデーションエラーが発生します。各商品の個別割引率は承認範囲内（製品A:20%まで、製品B:15%まで）ですが、見積書全体では保存できません。先週までは同様の見積書を作成できていました。",
            "resolution": "この問題は先週末にデプロイされた新しい検証ルールが原因でした。解決手順：\n1. システム管理者として設定 > カスタムオブジェクト > Quote > 検証ルール を確認\n2. 新しい検証ルール「Total_Discount_Approval_Required」が追加されていた\n3. このルールは「見積全体の割引合計額が100万円を超える場合、承認者フィールドは必須」という条件\n4. 当該見積の合計割引額：(1,000,000 * 10 * 0.15) + (200,000 * 10 * 0.1) = 1,700,000円\n5. 見積フォームの「承認者」フィールドに営業マネージャー名を入力\n6. または割引率を調整して合計割引額を100万円以下に抑える方法もある\n7. Release Notes確認：今回のルール変更はコンプライアンス要件に基づくもの\nこれにより見積書が正常に保存できるようになりました。また、営業部門に対して新しい割引承認ルールについての周知を行い、見積作成プロセスのトレーニング資料を更新しました。",
            "error_code": "FIELD_CUSTOM_VALIDATION_EXCEPTION",
            "affected_version": "Spring '21"
        },
        # SAP ERP - 生産管理 - 製造指示
        {
            "system_name": "SAP ERP",
            "category": "生産管理",
            "subcategory": "製造指示",
            "module": "PP-SFC",
            "short_description": "製造指図作成（CO01）で「BAPI_OBJCL_CREATE の実行中にエラーが発生しました」と表示される",
            "description": "トランザクションCO01で製造指図を作成しようとすると、保存時に「BAPI_OBJCL_CREATE の実行中にエラーが発生しました」というエラーメッセージが表示され、製造指図の作成が完了しません。具体的な操作手順：\n1. CO01を起動し、オーダータイプPP01を選択\n2. 材料番号FG-1000（完成品）、プラント1000、数量1000個を入力\n3. 作業計画に標準のルーティングを割り当て\n4. 基本日付に現在日を設定し、製造開始予定日を来週月曜日に設定\n5. 「保存」をクリック\nこの時点でエラーが発生し、指図番号が採番されません。同様の手順で先週までは製造指図を作成できていました。対象材料には有効なBoM（部品表）とルーティングが存在します。",
            "resolution": "この問題はSAPシステムの分類システム（Classification System）の関連テーブルにデータ不整合が発生したことが原因でした。解決手順：\n1. トランザクションST22でダンプログを分析し、テーブルCLCLASSINDEXに関する問題を特定\n2. トランザクションCL6Nで分類システムの状態を確認\n3. SAP注意事項2853476を確認し、推奨された修正手順を実施:\n   a. トランザクションSE14でテーブルCLCLASSINDEXの整合性チェックを実行\n   b. 破損したインデックスエントリを特定し、クリーンアップレポートを実行\n   c. RSCLS_REORG_IDXレポートを実行して分類インデックスを再構築\n4. SAPサポートと連携し、ハイプライオリティメッセージを登録（メッセージ番号: 2023/5555555）\n5. 製造管理部門と協力し、緊急対応として別の製造管理方法を一時的に導入\nこれにより製造指図が正常に作成できるようになりました。また、分類システムの定期メンテナンスをシステム保守計画に追加し、同様の問題の再発を防止しました。",
            "error_code": "CL123",
            "affected_version": "ECC 6.0"
        },
        # Microsoft Dynamics 365 - 財務会計 - 会計レポート
        {
            "system_name": "Microsoft Dynamics 365",
            "category": "財務会計",
            "subcategory": "会計レポート",
            "module": "Financial Reporting",
            "short_description": "財務諸表レポートで部門別データが正しく表示されない",
            "description": "財務レポートワークスペースから「部門別損益計算書」レポートを実行すると、一部の部門（営業部門とマーケティング部門）のデータが正しく表示されません。問題の詳細：\n1. 財務 > レポート > 財務レポート > 「部門別損益計算書」を選択\n2. 期間：2023年4月、表示レベル：「詳細」を選択\n3. レポート表示後、営業部門とマーケティング部門の売上高と費用が0または異常に低い値で表示される\n4. 他の部門（製造、研究開発など）のデータは正常に表示される\n5. 元帳照会画面で確認すると、営業部門とマーケティング部門の取引データは正しく入力・転記されている\n6. 3月のレポートでは全部門のデータが正しく表示されていた\n経営会議で使用する資料のため、早急な対応が必要です。",
            "resolution": "この問題は4月に実施された組織構造変更後のレポート構成が適切に更新されていなかったことが原因でした。解決手順：\n1. Dynamics 365管理センター > レポート設計 でレポート定義を確認\n2. 「部門別損益計算書」のレポート定義で使用されている組織階層を確認\n3. 4月1日付けで営業部門とマーケティング部門が「デジタルビジネス本部」という新しい上位組織に再編されていた\n4. レポート定義の行定義で部門コードが直接指定されており、新組織構造を反映していなかった\n5. Financial Reporter Designerでレポート定義を修正:\n   a. 行定義で部門コードをハードコーディングせず、組織階層から動的に取得するよう変更\n   b. 新しい組織階層「BU_HIERARCHY_2023」を参照するよう設定\n   c. レポート定義を保存し再デプロイ\n6. Microsoft Support Article KB4599823を参照し、設定を検証\nこれによりレポートが正しいデータを表示するようになりました。また、組織変更プロセスのチェックリストに「財務レポート定義の見直し」項目を追加し、今後の組織変更時に自動的に対応できるよう手順を整備しました。",
            "error_code": "FRX-0023",
            "affected_version": "2021 Release Wave 1"
        },
    ]
    
    # サンプルデータの生成
    for i in range(1, count + 1):
        # インシデント番号の生成
        incident_number = f"INC{i:05d}"
        
        # ランダムな日時（過去30日以内）
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        created_at = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        
        # インシデントデータをランダムに選択するか、なければ生成
        if i <= len(incidents_data):
            # 既存テンプレートを使用
            incident = incidents_data[i-1]
            system_name = incident["system_name"]
            category = incident["category"]
            subcategory = incident["subcategory"]
            module = incident["module"]
            short_description = incident["short_description"]
            description = incident["description"]
            error_code = incident["error_code"]
            affected_version = incident["affected_version"]
            
            # ステータスをランダムに選択（古いインシデントは解決済みの確率を高く）
            if days_ago > 20:
                status = random.choices(statuses, weights=[5, 10, 40, 45])[0]
            elif days_ago > 10:
                status = random.choices(statuses, weights=[10, 20, 40, 30])[0]
            else:
                status = random.choices(statuses, weights=[30, 40, 20, 10])[0]
                
            # 修正: 事前定義されたインシデントはステータスに関わらず常にresolutionを設定
            resolution = incident["resolution"]
        else:
            # ランダムに生成
            system_name = random.choice(systems)
            category = random.choice(list(categories_modules.keys()))
            subcategory = random.choice(categories_modules[category]["subcategories"])
            
            # システムに対応するモジュールを選択
            available_modules = categories_modules[category]["modules"].get(system_name, ["標準モジュール"])
            module = random.choice(available_modules)
            
            # バージョンを選択
            affected_version = random.choice(versions.get(system_name, ["最新版"]))
            
            # エラーコードを生成
            if system_name == "SAP ERP":
                error_code = f"{random.choice(['ABAP', 'MM', 'FI', 'SD', 'PP'])}{random.randint(100, 999)}"
            elif system_name == "Oracle EBS":
                error_code = f"ORA-{random.randint(10000, 99999)}"
            elif system_name == "Microsoft Dynamics 365":
                error_code = f"D365-{random.randint(1000, 9999)}"
            elif system_name == "Infor CloudSuite":
                error_code = f"INF-{random.randint(1000, 9999)}"
            elif system_name == "Salesforce":
                error_code = f"SFDC-{random.randint(1000, 9999)}"
            else:
                error_code = f"ERR-{random.randint(1000, 9999)}"
            
            # ステータスをランダムに選択
            if days_ago > 20:
                status = random.choices(statuses, weights=[5, 10, 40, 45])[0]
            elif days_ago > 10:
                status = random.choices(statuses, weights=[10, 20, 40, 30])[0]
            else:
                status = random.choices(statuses, weights=[30, 40, 20, 10])[0]
                
            # 基本情報の生成
            short_description = f"{module}で{subcategory}処理実行時にエラー発生"
            description = f"{system_name}の{module}モジュールで{subcategory}機能を使用中にエラーが発生しました。{error_code}というエラーコードが表示され、処理を完了できません。詳細な調査が必要です。"
            
            # ランダム生成の場合は従来通りステータスによって分岐
            resolution = f"原因はシステム設定の不整合でした。{module}の設定画面で正しいパラメータを指定し、問題を解決しました。今後の予防策として、定期的な設定チェックを推奨します。" if status in ["解決済み", "クローズ"] else ""
        
        # 優先度（カテゴリに応じて重み付け）
        if category in ["財務会計", "システム管理"]:
            priority = random.choices(priorities, weights=[50, 30, 20])[0]
        else:
            priority = random.choices(priorities, weights=[20, 50, 30])[0]
        
        # 担当者
        if category in assignees:
            assigned_to = random.choice(assignees[category])
        else:
            assigned_to = random.choice([name for sublist in assignees.values() for name in sublist])
        
        # 更新日時（作成日時以降、状態に応じて）
        if status == "新規":
            updated_at = created_at
        else:
            # 作成日時以降、現在までの間のランダムな時間
            max_days_later = min(days_ago, 7)  # 最大7日後または作成からの経過日数
            days_later = random.randint(0, max_days_later)
            hours_later = random.randint(0, 23) if days_later < max_days_later else random.randint(0, hours_ago)
            updated_at = created_at + timedelta(days=days_later, hours=hours_later)
        
        # データをDBに挿入
        cursor.execute('''
        INSERT INTO incidents (
            incident_number, created_at, status, priority, category, subcategory,
            system_name, module, short_description, description, resolution, 
            assigned_to, updated_at, error_code, affected_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            incident_number, created_at.strftime('%Y-%m-%d %H:%M:%S'), 
            status, priority, category, subcategory,
            system_name, module, short_description, description, resolution, 
            assigned_to, updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            error_code, affected_version
        ))


if __name__ == "__main__":
    setup_database()
    print("基幹系システム問い合わせデータベースの作成が完了しました。")