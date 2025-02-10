from pydantic import BaseModel, Field


class CompanyResearch(BaseModel):
    business_overview: str = Field(description="企業の事業概要について、提供する製品やサービス、主要な顧客層、業界内でのポジショニングなどを含め、具体的かつ詳細に説明してください。可能な場合は、具体例や数値データも盛り込み、企業の全体像が分かるように記述すること。")
    revenue: str = Field(description="直近の年度や期間の売上額を明記してください。成長率や前年との比較、主要な収益源がある場合は、その点についても触れてください。")
    num_employees: str = Field(description="正社員および契約社員の人数が記載されている場合は、それぞれの数値を抽出してまとめること。人数が複数の部門や拠点に分かれている場合は、可能な限りそれぞれの情報も含めること。")    
    executive_officers: list[str] = Field(description="企業の執行役員に関して、氏名、役職、経歴などの情報を全員分抽出してください。可能であれば、各役員の担当分野や経歴の要点も合わせて記述すること。")
    organizational_structure: str = Field(description="企業の組織構造や内部統制の仕組みについて、主要な部署、指揮命令系統、組織の機能分担などを体系的に漏れなく記述してください。分かりやすく整理することが重要です。")
    locations: str = Field(description="本社、国内外の支店、子会社、提携先など、記載されている全ての拠点情報を抽出してください。所在地、役割、規模などの補足情報があれば併記すること。")
    corporate_strategy: str = Field(description="企業が掲げる中長期的な戦略、ビジョン、経営目標、競争優位性の確保に向けた具体的な施策など、企業戦略全般に関する情報を網羅的に記述してください。")
    service_overview: str = Field(description="企業が提供しているサービスについて、特徴、提供価値、主要な機能や利点などを抜け漏れなく詳細にまとめてください。")
    service_competitors: list[str] = Field(description="企業が提供しているサービスに関して、その主要な競合の企業名と競合サービス名を抽出し、どのようなサービスかまで記述すること。")
    recruitment_strategy: str = Field(description="企業の採用方針やプロセス、募集職種、採用後の育成プログラムなど、採用戦略に関する情報を具体的に記述してください。")
    recruitment_status: str = Field(description="企業の採用状況について、採用人数、募集ポジション、進捗状況など、企業の採用活動全体の現状をマークダウン形式でまとめてください。")
    recruitment_articles: list[str] = Field(description="自社の採用計画に関するインタビュー記事や事例記事のURLを記述し、その内容について詳細を具体的にマークダウン形式で記述してください。")
    contracted_recruitment_systems: str = Field(description="自社の採用活動で取り入れている採用システムや提携しているRPOについて、具体的なサービス名やRPO名と概要について記述し、導入背景や効果などが言及されている場合は具体的に抽出すること。")
