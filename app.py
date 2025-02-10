import os
import random
import re
import time

from bs4 import BeautifulSoup
from chalice import Chalice, Response
from loguru import logger
from slack_bolt import App
from slack_bolt.response import BoltResponse
from slack_bolt.adapter.aws_lambda.chalice_handler import ChaliceSlackRequestHandler
from slack_bolt.adapter.aws_lambda.lambda_s3_oauth_flow import LambdaS3OAuthFlow

from chalicelib.research_company import research_company
from chalicelib.libs.slack_api.ui.modal.create_modal import open_modal
from chalicelib.libs.notion_api.create_page import add_page_to_notion_database

bolt_app = App(
    process_before_response=True,
    oauth_flow=LambdaS3OAuthFlow()
)

app = Chalice(app_name="recruta-gtm-dev-company-research")
slack_handler = ChaliceSlackRequestHandler(app=bolt_app, chalice=app)


@bolt_app.middleware
def skip_retry(logger, request, next):
    # https://github.com/slackapi/bolt-python/blob/main/slack_bolt/request/request.py#L15
    print(f"{request.headers=}")
    if "x-slack-retry-num" in request.headers:
        resp = BoltResponse(status=200, body="", headers={})
        return resp
    return next()

def acknowledge_anyway(ack):
    ack()


def handle_email_message(event, say):
    logger.info(f"{event=}")
    thread_ts = event.get("ts")
    channel = event.get("channel")
    files = event.get("files", [])
    if not files:
        return
    for file in files:
        if (file.get("filetype") != "email"):
            continue
        preview = file.get("preview", "")
        soup = BeautifulSoup(preview, "html.parser")
        text = "\n".join(soup.get_text(separator="\n", strip=True).split())
        if m := re.search("会社名\s+?(.*?)\s+?(部署|企業URL|部門)", text):
            company_name = m.group(1).strip()
            slack_url = file.get("permalink", "")
            timestamp = file.get("timestamp", "")
            from_address = file.get("from", [{}])[0].get("address", "")
            if not from_address.startswith("noreply@studio.site"):
                continue
            contents = []
            for (response_content, citations) in research_company(company_name):
                pattern = re.compile(r"<think>.*?</think>", re.DOTALL)
                content = pattern.sub("", response_content).strip()
                content = content.replace("```markdown", "").replace("```", "").replace("---", "")
                contents.append(content + "\n")
                for idx, citation in enumerate(citations, start=1):
                    contents.append(f"- [{idx}] {citation}")
                contents.append("\n")
            text += f"\nslack: {slack_url}" + f"\ntimestamp: {timestamp}"
            resp = add_page_to_notion_database("\n".join(contents), company_name, text)
            say(
                channel=channel,
                thread_ts=thread_ts,
                text="調査が完了しました",
                blocks=[
                    {
                        "type": "rich_text",
                        "elements": [
                            {
                                "type": "rich_text_section",
                                "elements": [
                                    {"type": "text", "text": f"{company_name} について調べました！\n"},
                                    {"type": "link", "url": resp.get("url"), "text": resp.get("url")}
                                ]
                            }
                        ]
                    }
                ]
            )


def run_research_operation(body, say):
    chunk_size = 2500
    time.sleep(5)
    event = body.get("event", {})
    request_content = re.sub(r"^<@(.+?)>", "", event.get("text", "")).strip()
    if not request_content:
        return
    logger.info(f"{event=}")
    logger.info(f"{request_content=}")
    for (response_content, citations) in research_company(request_content):
        pattern = re.compile(r"<think>.*?</think>", re.DOTALL)
        content = pattern.sub("", response_content).strip()
        content = content.replace("```markdown", "").replace("```", "").replace("---", "")
        chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
        citation_blocks = []
        for idx, citation in enumerate(citations, start=1):
            citation_blocks.append({
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_quote",
                        "elements": [{
                            "type": "link",
                            "url": citation,
                            "text": f"[{idx}] {citation}",
                        }],
                    }
                ]
            })
        for chunk in chunks:
            say(
                channel=event.get("channel"),
                thread_ts=event.get("event_ts"),
                text=chunk
            )
        say(
            channel=event.get("channel"),
            thread_ts=event.get("event_ts"),
            text="",
            blocks=citation_blocks,
        )

bolt_app.event("message")(
    ack=acknowledge_anyway,
    lazy=[handle_email_message],
)


# modal
def handle_modal(logger, body: dict, view: dict):
    print(f"[handle_modal] {type(body)=} {body=}")
    print(f"[handle_modal] {view=}")
    values = view.get("state", {}).get("values", {})
    blocks = view.get("blocks", [])
    if isinstance(values, dict) and len(blocks) >= 2:
        company_id = blocks[0]["block_id"]
        person_id = blocks[1]["block_id"]
        company_name = values.get(company_id, {}).get("company_name", {}).get("value", "")
        person_name = values.get(person_id, {}).get("person_name", {}).get("value", "")
        print(f"[handle_modal] {company_name=}")
        print(f"[handle_modal] {person_name=}")
        # 'respond' は response_url が存在しないため使用できません。代わりに、提出者へ DM を送信して通知します。
        user_id = body.get("user", {}).get("id")
        stamps = ["dancing-nya", "isogu-nya", "unun-nya", "mada-nya", "tekuteku-nya", "banzai-nya", "stretch-nya"]
        if user_id:
            slack_response = bolt_app.client.chat_postMessage(
                channel=os.getenv("SLACK_WORKFLOW_CHANNEL_ID"),
                text="リクエストを受け付けました",
                blocks=[
                    {
                        "type": "rich_text",
                        "elements": [
                            {
                                "type": "rich_text_section",
                                "elements": [
                                    {"type": "user", "user_id": user_id},
                                    {"type": "text", "text": " リクエストを受け付けました "},
                                    {"type": "emoji", "name": random.choice(stamps)},
                                    {"type": "text", "text": f"\n企業名: {company_name}\n担当者名: {person_name}"}
                                ]
                            }
                        ]
                    }
                ]
            )
            thread_ts = slack_response.data.get("ts")
            contents = []
            for (response_content, citations) in research_company(company_name):
                pattern = re.compile(r"<think>.*?</think>", re.DOTALL)
                content = pattern.sub("", response_content).strip()
                content = content.replace("```markdown", "").replace("```", "").replace("---", "")
                contents.append(content + "\n")
                for idx, citation in enumerate(citations, start=1):
                    contents.append(f"- [{idx}] {citation}")
                contents.append("\n")

            resp = add_page_to_notion_database("\n".join(contents), company_name, person_name)
            slack_response = bolt_app.client.chat_postMessage(
                channel=os.getenv("SLACK_WORKFLOW_CHANNEL_ID"),
                thread_ts=thread_ts,
                text="調査が完了しました",
                blocks=[
                    {
                        "type": "rich_text",
                        "elements": [
                            {
                                "type": "rich_text_section",
                                "elements": [
                                    {"type": "user", "user_id": user_id},
                                    {"type": "text", "text": " 調査が完了しました！\n"},
                                    {"type": "link", "url": resp.get("url"), "text": resp.get("url")}
                                ]
                            }
                        ]
                    }
                ]
            )
        else:
            logger.warning("ユーザーIDが取得できなかったため、通知メッセージの送信に失敗しました。")




bolt_app.command("/research")(
    ack=acknowledge_anyway,
    lazy=[open_modal],
)
bolt_app.view("modal-id")(
    ack=acknowledge_anyway,
    lazy=[handle_modal],
)




@app.route(
    "/slack/events",
    methods=["POST"],
    content_types=["application/x-www-form-urlencoded", "application/json"],
)
def events() -> Response:
    logger.info(f"{app.current_request=}")
    return slack_handler.handle(app.current_request)


@app.route("/slack/install", methods=["GET"])
def install() -> Response:
    return slack_handler.handle(app.current_request)


@app.route("/slack/oauth_redirect", methods=["GET"])
def oauth_redirect() -> Response:
    return slack_handler.handle(app.current_request)
