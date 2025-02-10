from slack_sdk .web import WebClient


def open_modal(body: dict, client: WebClient):
    # 入力項目ひとつだけのシンプルなモーダルを開く
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "modal-id",
            "title": {
                "type": "plain_text",
                "text": "企業情報のレポート生成",
            },
            "submit": {
                "type": "plain_text",
                "text": "Submit",
            },
            "close": {
                "type": "plain_text",
                "text": "キャンセル",
            },
            "blocks": [
                {
                    "type": "input",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "company_name",
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "企業名",
                    },
                },
                {
                    "type": "input",
                    "optional": True,
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "person_name",
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "担当者名",
                    },
                },
                # {
                #     "type": "section",
                #     "optional": True,
                #     "block_id": "prompt_select",
                #     "text": {"type": "mrkdwn", "text": "プロンプトを選択"},
                #     "accessory": {
                #         "type": "static_select",
                #         "action_id": "prompt_select",
                #         "placeholder": {"type": "plain_text", "text": "プロンプトを選択"},
                #         "options": [
                #             {"text": {"type": "plain_text", "text": "リクルタ商談"}, "value": "prompt_recruta"},
                #         ]
                #     }
                # }
            ],
        },
    )