import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from loguru import logger

from chalicelib.llms import openai_, perplexity
from chalicelib.models.company_research import CompanyResearch
from chalicelib.utils.load_prompt import load_prompt

load_dotenv()


def _get_information(
    company_name: str,
    schema_path: str,
    idx: int = 0,
) -> tuple[int, str, list[str], float]:
    prefix = os.path.basename(schema_path).split(".", 1)[0]
    system_message = load_prompt("chalicelib/prompts/research_items.jinja")
    schema = json.dumps(json.load(open(schema_path)), ensure_ascii=False, indent=4)
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"「{company_name}」について以下の情報を調べてください:\n{schema}"},
    ]
    response_content, citations, cost = perplexity.generate_response(messages)
    logger.debug(f"[{prefix}] {response_content=}")
    logger.debug(f"[{prefix}] {citations=}")
    logger.debug(f"[{prefix}] {cost=}")
    return idx, response_content, citations, cost


def _get_structured_company(
    company_name: str,
    result_company: str,
    citations_company: list[str],
    result_service: str,
    citations_service: list[str],
    result_recruitment: str,
    citations_recruitment: list[str],
) -> tuple[CompanyResearch, float]:
    system_message = load_prompt(
        "chalicelib/prompts/get_structured_company.jinja",
        company_name=company_name,
        result_company=result_company,
        citations_company=citations_company,
        result_service=result_service,
        citations_service=citations_service,
        result_recruitment=result_recruitment,
        citations_recruitment=citations_recruitment,
    )
    messages = [{"role": "system", "content": system_message}]
    company_reseach, cost = openai_.generate_structured_response(
        messages,
        CompanyResearch,
    )
    logger.debug(f"{company_reseach=}")
    logger.debug(f"{cost=}")
    return company_reseach, cost


def research_company(company_name: str):
    schema_paths = [
        "chalicelib/schema/company.json",
        "chalicelib/schema/recruitment.json",
        "chalicelib/schema/service.json",
    ]

    total_cost = 0.0
    # results = []
    # for schema_path in schema_paths:
    #     idx, response_content, citations, cost = _get_information(company_name, schema_path)
    #     total_cost += cost
    #     results.append((response_content, citations))
    _results = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(_get_information, company_name, schema_path, idx=idx)
            for idx, schema_path in enumerate(schema_paths)
        ]
        for future in as_completed(futures):
            idx, response_content, citations, cost = future.result()
            total_cost += cost
            _results.append((idx, response_content, citations))
    results = [(res[1], res[2]) for res in sorted(_results, key=lambda x: x[0])]
    return results
    # company_research, cost = _get_structured_company(
    #     company_name=company_name,
    #     result_company=results[0][0],
    #     citations_company=results[0][1],
    #     result_service=results[1][0],
    #     citations_service=results[1][1],
    #     result_recruitment=results[2][0],
    #     citations_recruitment=results[2][1],
    # )
    # total_cost += cost
    # logger.debug(f"{total_cost=}")
    # logger.debug(f"{company_research=}")
    # return company_research



if __name__ == "__main__":
    company_research = research_company("株式会社Algomatic")
    print(company_research)
