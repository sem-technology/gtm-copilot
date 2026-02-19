# GTM Copilot

このプロジェクトでは、AIを活用してGoogleタグマネージャー（GTM）の実装作業を自動化するためのプログラムやプロンプトを構築しています。

## 主な仕組み

1. **抽出**: GoogleタグマネージャーAPIを使用して、既存のタグ、トリガー、変数などのコンポーネントを取得し、JSON形式で保存します。
2. **AIによる修正**: AIを使用してJSONファイルを更新し、実際のタグ実装ロジックをファイル上で行います。
3. **同期**: 実装（JSONの編集）が完了したら、APIを使用して変更をGoogleタグマネージャーに同期させます。

## アーキテクチャ

ポータビリティとセットアップの容易さを確保するため、このプロジェクトは**Python標準ライブラリのみ**を使用して実装されています。外部依存ライブラリ（`requests`や`google-auth`など）は不要です。

- **プログラミング言語**: Python 3.x（標準ライブラリのみ）

## Agent Skills のセットアップ

Agent Skills の全般的な情報については [agentskills.io](https://agentskills.io/home) を参照してください。

GTM Copilot のスキルを使用するには、以下の手順を実行してください：

1. **ダウンロード**: [Releases](https://github.com/sem-technology/gtm-copilot/releases) ページからビルド済みの `gtm-copilot_vX.X.X.zip` を取得します。
2. **配置**: Zip ファイルを解凍し、中身を AI エージェントのスキルディレクトリ（例: `.agent/skills/gtm-copilot/`）に配置します。
3. **認証**: `.agent/skills/gtm-copilot/.env.example`をコピーし、`.agent/skills/gtm-copilot/.env`を作成、中身の認証情報を更新します。
3. **利用**: 配置が完了すると、AI エージェントは `SKILL.md` に定義されたツールを自動的に認識し、GTM の自動化作業を開始できるようになります。
