# GTM Copilot

このプロジェクトでは、AIを活用してGoogleタグマネージャー（GTM）の実装作業を自動化するためのプログラムやプロンプトを構築しています。

## 主な仕組み

1. **抽出**: GoogleタグマネージャーAPIを使用して、既存のタグ、トリガー、変数などのコンポーネントを取得し、JSON形式で保存します。
2. **AIによる修正**: AIを使用してJSONファイルを更新し、実際のタグ実装ロジックをファイル上で行います。
3. **同期**: 実装（JSONの編集）が完了したら、APIを使用して変更をGoogleタグマネージャーに同期させます。

## アーキテクチャ

ポータビリティとセットアップの容易さを確保するため、このプロジェクトは**Python標準ライブラリのみ**を使用して実装されています。外部依存ライブラリ（`requests`や`google-auth`など）は不要です。

- **プログラミング言語**: Python 3.x（標準ライブラリのみ）

## セットアップ (Agent Skills)

GTM CopilotをAIエージェントのスキルとして使用するには、以下の手順を実行してください：

1. **ダウンロード**: このリポジトリをエージェントのスキルディレクトリにクローンします。

   **Claude Codeの場合:**
   ```sh
   # ユーザーレベル（全プロジェクトで有効）
   git clone https://github.com/sem-technology/gtm-copilot.git ~/.claude/skills/gtm-copilot
   # プロジェクトレベル（特定のプロジェクトのみで有効）
   git clone https://github.com/sem-technology/gtm-copilot.git .claude/skills/gtm-copilot
   ```

   **Gemini（Antigravity等）の場合:**
   ```sh
   # ユーザーレベル（全プロジェクトで有効）
   git clone https://github.com/sem-technology/gtm-copilot.git ~/.agent/skills/gtm-copilot
   # プロジェクトレベル（特定のプロジェクトのみで有効）
   git clone https://github.com/sem-technology/gtm-copilot.git .agent/skills/gtm-copilot
   ```

2. **認証**: 
   - スキルディレクトリ内の `.env.example` をコピーして `.env` を作成します。
   - 認証トークンを生成するために以下のスクリプトを実行します：
     ```sh
     python scripts/bin/auth.py
     ```
   - 表示される手順に従って認証を行い、取得した値を `.env` ファイルに設定します。

3. **利用**: 配置と認証が完了すると、AIエージェントは `SKILL.md` に定義されたツールを自動的に認識し、GTMの自動化作業を開始できるようになります。

## アップデート

スキルを最新バージョンに更新するには、スキルディレクトリに移動して以下を実行してください：

```sh
# ユーザーレベル（例）
cd ~/.agent/skills/gtm-copilot
git pull origin main
```

Agent Skillsの全般的な情報については [agentskills.io](https://agentskills.io/home) を参照してください。
