# Agnoを使ったマルチエージェントシステムツール

## 概要

このサンプルプログラムは、ITサポートチームがサポートリクエストの処理を自動化するマルチエージェント機能を搭載しています。

1. ユーザークエリから重要な情報を抽出
2. 類似の問題と解決策について既存のデータベースを検索
3. 新しい問題に対するウェブベースの調査を生成
4. 詳細な解決策を含む包括的なレポートを作成


## 機能

- **キーワード抽出**: ユーザークエリから技術用語、エラーコード、システム名を自動的に識別
- **クエリ生成**: 抽出されたキーワードを最適化されたSQLクエリに変換
- **データベース検索**: 過去のインシデントと解決策のナレッジベースを検索
- **ウェブ調査**: データベースに見つからない問題についてオンライン調査を実施
- **レポート生成**: 完全な情報と解決策を含む詳細な構造化レポートを作成

## アーキテクチャ

システムは5つの特化したエージェントによるマルチエージェントアーキテクチャを使用しています：

1. **キーワード抽出エージェント**: ユーザークエリから重要な技術用語を抽出
2. **SQLクエリ生成エージェント**: 抽出されたキーワードに基づいてSQLクエリを作成
3. **SQLクエリ実行エージェント**: インシデントデータベースに対してクエリを実行
4. **ウェブ検索エージェント**: データベース結果が不十分な場合にウェブベースの調査を実施
5. **レポート生成エージェント**: 収集したすべての情報を組み合わせた包括的なレポートを作成

## 前提条件

- Python 3.8以上
- SQLite
- OpenAI APIキー
- Exa APIキー（ウェブ検索機能用）

## インストール

1. リポジトリをクローン：
```bash
git clone https://github.com/sinjorjob/agno-multi-agent-sample.git
cd agno-multi-agent-sample
```

2. 依存関係をインストール：
```bash
pip install -r requirements.txt
```

3. APIキーの環境変数を設定（またはコード内で直接変更）：
```bash
# agent.pyファイル内で、これらを実際のAPIキーに置き換えてください
api_key = "sk-pxxxxxxxxxxxxxx"  # OpenAI APIキー
exa_api_key = "xxxxxxxxxxx"     # Exa APIキー
```

## デモデータベースのセットアップ

このリポジトリには、テスト用のサンプルITインシデントを含むデモデータベースを作成するスクリプトが含まれています：

1. データベース作成スクリプトを実行：
```bash
python create_db.py
```

これにより以下が実行されます：
- `.db`ディレクトリに`it_support.db` SQLiteデータベースを作成
- 様々なITシステム（SAP ERP、Oracle EBS、Microsoft Dynamics 365など）をカバーする30の現実的なサンプルインシデントを生成
- 詳細な説明、エラーコード、解決策を含むデータベースを構築

## ディレクトリ構造

```
📁 .db
└─📄 it_support.db         # インシデントレコードを含むSQLiteデータベース

📁 reports                  # 生成されたインシデントレポートが保存されるディレクトリ

📁 temp_files               # 処理中に使用される一時ファイル
├─📄 generated_sql_query.txt
├─📄 original_query.txt
└─📄 sql_results.json
```

## 使用方法

システムを使用するには：

1. `agent.py`ファイルをAPIキーで変更
2. テストクエリでエージェントを実行：
```bash
python agent.py
```

試すことができるサンプルクエリ：
- "給与計算バッチを実行したところ、「BenefitAccrualCalculationFailedException」というエラーメッセージが表示される"
- "SAP ERPの財務会計モジュールでFB01の伝票登録時に消費税が自動計算されません"

## 動作の仕組み

1. ユーザーがITサポートクエリを送信
2. システムがクエリから重要な技術用語を抽出
3. これらの用語を使用してインシデントデータベースを検索するSQLクエリを生成
4. 類似のインシデントが見つかった場合、その詳細と解決策を取得
5. データベースで一致するものが見つからない場合、ウェブ調査を実施
6. すべての情報を包括的なレポートにまとめる
7. レポートはタイムスタンプ付きのファイル名で`reports`ディレクトリに保存

## エージェント設計

システム内の各エージェントには特化した役割があります：

- **キーワード抽出エージェント**: システム名、エラーコード、モジュール名、機能名、カテゴリを識別
- **SQLクエリ生成エージェント**: 部分一致のためのLIKE演算子を使用して最適化されたSQLクエリを作成
- **SQLクエリ実行エージェント**: クエリを実行し、結果をJSONとして保存
- **ウェブ検索エージェント**: Exa APIを使用してオンラインで関連情報を検索
- **レポート生成エージェント**: 完全なインシデント情報を含む詳細なMarkdownレポートを作成

## サンプル出力

システムは、日付と関連キーワードを含むファイル名で`reports`ディレクトリに保存される、Markdown形式の詳細なレポートを生成します。

### キーワード抽出の出力例

```
給与計算, バッチ, BenefitAccrualCalculationFailedException, エラーメッセージ
```

### 生成されるSQLクエリの例 (generated_sql_query.txt)

```sql
SELECT * FROM incidents 
WHERE short_description LIKE '%給与計算%' OR description LIKE '%給与計算%' OR resolution LIKE '%給与計算%' OR error_code LIKE '%給与計算%' 
OR short_description LIKE '%バッチ%' OR description LIKE '%バッチ%' OR resolution LIKE '%バッチ%' OR error_code LIKE '%バッチ%' 
OR short_description LIKE '%BenefitAccrualCalculationFailedException%' OR description LIKE '%BenefitAccrualCalculationFailedException%' 
OR resolution LIKE '%BenefitAccrualCalculationFailedException%' OR error_code LIKE '%BenefitAccrualCalculationFailedException%' 
OR short_description LIKE '%エラーメッセージ%' OR description LIKE '%エラーメッセージ%' OR resolution LIKE '%エラーメッセージ%' 
OR error_code LIKE '%エラーメッセージ%' 
ORDER BY incident_number DESC LIMIT 5;
```

### SQL実行結果の例 (sql_results.json)

```json
[
  {
    "incident_number": "INC00008",
    "system_name": "Microsoft Dynamics 365",
    "module": "Human Resources",
    "short_description": "給与計算処理で「福利厚生費の累計計算エラー」が発生",
    "description": "6月の給与計算バッチを実行したところ、「BenefitAccrualCalculationFailedException: Failed to calculate benefit balance for employee 000352」というエラーメッセージが表示され、処理が中断されました。問題の詳細：\n1. 人事 > 定期処理 > 給与計算から給与計算バッチを実行\n2. 処理開始後10分でエラーが発生し、該当社員ID 000352の処理で停止\n3. 給与計算ログファイルに福利厚生費の累計計算に関するエラーが記載されている\n4. 該当社員の福利厚生プランは「標準健康保険プラン」と「選択型退職金プラン」\n5. 5月までの給与計算は正常に処理されていた\n6. 先月該当社員の雇用形態が変更された（契約社員から正社員へ）\n給与計算実行日が迫っており、早急な解決が必要です。",
    "resolution": "この問題は雇用形態変更時の福利厚生プラン移行処理が不完全だったことが原因でした。以下の手順で解決しました：\n1. PowerShellを使用して詳細なエラーログを取得・分析\n2. 該当社員ID 000352の福利厚生スタートデータを確認し、雇用形態変更前の契約社員用プラン情報が残存していることを発見\n3. 人事 > 該当社員 > 福利厚生 で該当社員の重複登録を確認\n4. バッチエンドでのHcmEmployeeBenefitデータの終了日を設定した旧プランレコードを特定\n5. Microsoft Dynamics Support Article KB4598232を参照し、正しい修正手順を確認\n6. 福利厚生管理画面から旧プランの終了処理を適切に実施（終了日を雇用形態変更日として設定）\n7. システム管理者権限でBenefit Calculation Cacheをリセット\n8. 給与計算バッチを再実行\nこれにより給与計算が正常に完了しました。また、雇用形態変更時の福利厚生プラン移行処理を見直し、適切に実施されるように定期的なメンテナンスを行うことを確認しました。",
    "error_code": "BenefitAccrualCalculationFailedException",
    "affected_version": "2020 Release Wave 2"
  }
]
```

### 最終レポートの例 (reports/report_20240330_BenefitAccrual.md)

```markdown
# Microsoft Dynamics 365の給与計算バッチエラー調査レポート

## 概要
Microsoft Dynamics 365の給与計算バッチ実行時に発生する「BenefitAccrualCalculationFailedException」エラーの調査結果です。問題は雇用形態変更時の福利厚生プラン移行処理の不完全さが原因であることが判明しました。

## 問い合わせ詳細
給与計算バッチを実行したところ、「BenefitAccrualCalculationFailedException」というエラーメッセージが表示される

## 調査結果
データベース検索の結果、類似したインシデント記録が見つかりました（INC00008）。これは、Microsoft Dynamics 365のHuman Resourcesモジュールで発生した給与計算処理の問題に関するものです。

該当インシデントでは、雇用形態変更（契約社員から正社員）を行った従業員の給与計算バッチ処理時に「BenefitAccrualCalculationFailedException」エラーが発生し処理が中断されています。

### 問題の根本原因
雇用形態変更時の福利厚生プラン移行処理が不完全だったことが原因です。雇用形態変更前の契約社員用プラン情報が残存していたため、新しい正社員としての福利厚生計算時に矛盾が発生していました。

## データベースレコードの詳細情報

| フィールド | 値 |
|------------|-----|
| incident_number | INC00008 |
| system_name | Microsoft Dynamics 365 |
| module | Human Resources |
| short_description | 給与計算処理で「福利厚生費の累計計算エラー」が発生 |
| description | 6月の給与計算バッチを実行したところ、「BenefitAccrualCalculationFailedException: Failed to calculate benefit balance for employee 000352」というエラーメッセージが表示され、処理が中断されました。問題の詳細：<br>1. 人事 > 定期処理 > 給与計算から給与計算バッチを実行<br>2. 処理開始後10分でエラーが発生し、該当社員ID 000352の処理で停止<br>3. 給与計算ログファイルに福利厚生費の累計計算に関するエラーが記載されている<br>4. 該当社員の福利厚生プランは「標準健康保険プラン」と「選択型退職金プラン」<br>5. 5月までの給与計算は正常に処理されていた<br>6. 先月該当社員の雇用形態が変更された（契約社員から正社員へ）<br>給与計算実行日が迫っており、早急な解決が必要です。 |
| resolution | この問題は雇用形態変更時の福利厚生プラン移行処理が不完全だったことが原因でした。以下の手順で解決しました：<br>1. PowerShellを使用して詳細なエラーログを取得・分析<br>2. 該当社員ID 000352の福利厚生スタートデータを確認し、雇用形態変更前の契約社員用プラン情報が残存していることを発見<br>3. 人事 > 該当社員 > 福利厚生 で該当社員の重複登録を確認<br>4. バッチエンドでのHcmEmployeeBenefitデータの終了日を設定した旧プランレコードを特定<br>5. Microsoft Dynamics Support Article KB4598232を参照し、正しい修正手順を確認<br>6. 福利厚生管理画面から旧プランの終了処理を適切に実施（終了日を雇用形態変更日として設定）<br>7. システム管理者権限でBenefit Calculation Cacheをリセット<br>8. 給与計算バッチを再実行<br>これにより給与計算が正常に完了しました。また、雇用形態変更時の福利厚生プラン移行処理を見直し、適切に実施されるように定期的なメンテナンスを行うことを確認しました。 |
| error_code | BenefitAccrualCalculationFailedException |
| affected_version | 2020 Release Wave 2 |

## 解決策

データベースに記録された解決策に基づき、以下の手順での対応を推奨します：

1. **詳細なエラー情報の収集**
   - PowerShell診断ツールを使用して詳細なエラーログを取得・分析

2. **福利厚生データの確認**
   - 該当社員の福利厚生登録データを確認し、雇用形態変更前のプラン情報が残存していないか調査
   - 人事 > 従業員 > 福利厚生 メニューで該当社員の登録状況を確認

3. **福利厚生プランの修正**
   - 福利厚生管理画面から旧プランの終了処理を適切に実施
   - 終了日を雇用形態変更日に設定

4. **システムキャッシュのリセット**
   - システム管理者権限でBenefit Calculation Cacheをリセット

5. **バッチ処理の再実行**
   - 給与計算バッチを再実行

6. **長期的な改善策**
   - 雇用形態変更手順書を更新し、福利厚生プラン移行の正しい手続きを明確化
   - 雇用形態変更時のチェックリストに福利厚生プラン移行のチェック項目を追加

Microsoft Dynamics Support Article KB4598232を参照し、正確な手順を確認することをお勧めします。

## 参考情報
- Microsoft Dynamics 365 Human Resources モジュールのバージョン: 2020 Release Wave 2
- エラーコード: BenefitAccrualCalculationFailedException
- 関連サポート記事: KB4598232
```

