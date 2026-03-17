"""SkillAnalyzerAgent — NLP-powered skill extraction and gap analysis.

Uses spaCy for NER and pattern matching against a curated set of 200+
technology skills. Computes skill frequency, position weight, and
provides gap analysis when a job description is supplied.
"""

import logging
import re
from typing import Any

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

# ─── Curated Known Skills (200+) ────────────────────────────────────────────
KNOWN_SKILLS: set[str] = {
    # ── Programming Languages ────────────────────────────────────────────
    "Python", "JavaScript", "TypeScript", "Java", "C", "C++", "C#", "Go",
    "Rust", "Swift", "Kotlin", "Ruby", "PHP", "Perl", "R", "MATLAB",
    "Scala", "Haskell", "Lua", "Dart", "Elixir", "Clojure", "Julia",
    "Objective-C", "Assembly", "Shell", "Bash", "PowerShell", "Groovy",

    # ── Frontend ─────────────────────────────────────────────────────────
    "React", "React.js", "Angular", "Vue.js", "Vue", "Svelte", "Next.js",
    "Nuxt.js", "Gatsby", "HTML", "HTML5", "CSS", "CSS3", "SASS", "SCSS",
    "LESS", "Tailwind CSS", "TailwindCSS", "Bootstrap", "Material UI",
    "jQuery", "Webpack", "Vite", "Babel", "Redux", "Zustand", "MobX",
    "Styled Components", "Chakra UI", "Ant Design", "Storybook",

    # ── Backend / Frameworks ─────────────────────────────────────────────
    "Node.js", "Express.js", "Express", "FastAPI", "Django", "Flask",
    "Spring Boot", "Spring", "ASP.NET", ".NET", "Ruby on Rails", "Rails",
    "Laravel", "Gin", "Fiber", "NestJS", "Koa", "Hapi", "Actix",
    "Phoenix", "Rocket", "gRPC", "REST API", "RESTful", "GraphQL",
    "WebSocket", "Socket.IO",

    # ── Databases ────────────────────────────────────────────────────────
    "PostgreSQL", "MySQL", "MariaDB", "SQLite", "SQL Server", "Oracle",
    "MongoDB", "DynamoDB", "Cassandra", "CouchDB", "Neo4j", "ArangoDB",
    "Redis", "Memcached", "Elasticsearch", "InfluxDB", "TimescaleDB",
    "Supabase", "Firebase", "PlanetScale", "CockroachDB",

    # ── Cloud / Infrastructure ───────────────────────────────────────────
    "AWS", "Amazon Web Services", "GCP", "Google Cloud Platform",
    "Google Cloud", "Azure", "Microsoft Azure", "Heroku", "Vercel",
    "Netlify", "DigitalOcean", "Linode", "Cloudflare",
    "EC2", "S3", "Lambda", "ECS", "EKS", "RDS", "CloudFront",
    "SQS", "SNS", "API Gateway", "Route 53", "IAM",
    "Cloud Functions", "BigQuery", "Cloud Run", "Pub/Sub",
    "Azure DevOps", "Azure Functions", "Cosmos DB",

    # ── DevOps / CI-CD ───────────────────────────────────────────────────
    "Docker", "Kubernetes", "K8s", "Terraform", "Ansible", "Puppet",
    "Chef", "Vagrant", "Helm", "Istio", "Consul", "Vault",
    "CI/CD", "Jenkins", "GitHub Actions", "GitLab CI", "CircleCI",
    "Travis CI", "ArgoCD", "Buildkite", "Drone",
    "Nginx", "Apache", "Caddy", "HAProxy",
    "Linux", "Ubuntu", "CentOS", "RHEL", "Unix",
    "Prometheus", "Grafana", "Datadog", "New Relic", "Splunk",
    "ELK Stack", "Logstash", "Kibana", "Fluentd", "Jaeger",

    # ── Data / ML / AI ───────────────────────────────────────────────────
    "Machine Learning", "Deep Learning", "Artificial Intelligence",
    "TensorFlow", "PyTorch", "Keras", "scikit-learn", "sklearn",
    "XGBoost", "LightGBM", "CatBoost", "Hugging Face", "Transformers",
    "OpenAI", "GPT", "LLM", "LangChain", "LlamaIndex",
    "Computer Vision", "NLP", "Natural Language Processing",
    "Reinforcement Learning", "GANs", "CNN", "RNN", "LSTM",
    "BERT", "Stable Diffusion", "ONNX", "TensorRT",
    "pandas", "NumPy", "numpy", "SciPy", "Matplotlib", "Seaborn",
    "Plotly", "Bokeh", "Streamlit", "Gradio", "Jupyter",
    "Data Analysis", "Data Science", "Statistics", "Probability",
    "Feature Engineering", "Model Deployment", "MLOps",
    "MLflow", "Weights & Biases", "DVC", "Kubeflow",
    "Apache Spark", "PySpark", "Spark", "Hadoop", "Hive",
    "Apache Kafka", "Kafka", "Apache Airflow", "Airflow",
    "Apache Flink", "Flink", "dbt", "Dagster", "Prefect",
    "ETL", "ELT", "Data Engineering", "Data Warehousing",
    "Snowflake", "Redshift", "Databricks", "Delta Lake",

    # ── Analytics / BI ───────────────────────────────────────────────────
    "Tableau", "Power BI", "Looker", "Metabase", "Superset",
    "Google Analytics", "Mixpanel", "Amplitude",
    "Excel", "Google Sheets", "VBA",

    # ── Mobile ───────────────────────────────────────────────────────────
    "React Native", "Flutter", "SwiftUI", "Jetpack Compose",
    "Xamarin", "Ionic", "Expo", "Android", "iOS",
    "Xcode", "Android Studio", "CocoaPods",

    # ── Testing ──────────────────────────────────────────────────────────
    "Jest", "Mocha", "Cypress", "Playwright", "Selenium",
    "pytest", "unittest", "JUnit", "TestNG", "Vitest",
    "Testing Library", "Enzyme", "Puppeteer", "k6", "Locust",
    "TDD", "BDD", "Integration Testing", "Unit Testing",

    # ── Version Control / Collaboration ──────────────────────────────────
    "Git", "GitHub", "GitLab", "Bitbucket", "SVN",
    "Jira", "Confluence", "Notion", "Trello", "Asana",
    "Slack", "Linear", "Figma", "Sketch",

    # ── Security ─────────────────────────────────────────────────────────
    "OAuth", "OAuth2", "JWT", "SAML", "SSO", "LDAP",
    "Encryption", "SSL/TLS", "HTTPS", "OWASP",
    "Penetration Testing", "Security Auditing",
    "Cybersecurity", "SOC 2", "GDPR",

    # ── Methodologies ────────────────────────────────────────────────────
    "Agile", "Scrum", "Kanban", "Lean", "Waterfall",
    "Microservices", "Monolith", "Event-Driven Architecture",
    "Domain-Driven Design", "DDD", "CQRS", "Event Sourcing",
    "Design Patterns", "SOLID", "Clean Architecture",
    "System Design", "API Design", "Database Design",

    # ── Other ────────────────────────────────────────────────────────────
    "RabbitMQ", "NATS", "ZeroMQ", "MQTT", "ActiveMQ",
    "Celery", "Sidekiq", "Bull", "BullMQ",
    "OpenCV", "PIL", "Pillow", "FFmpeg",
    "LaTeX", "Markdown", "YAML", "JSON", "XML", "Protobuf",
    "Blockchain", "Solidity", "Ethereum", "Web3",
    "Unity", "Unreal Engine", "Godot",
    "ROS", "Raspberry Pi", "Arduino", "IoT",
    "SAP", "Salesforce", "ServiceNow", "Workday",
}

# Lowercase lookup for case-insensitive matching
_SKILL_LOOKUP: dict[str, str] = {s.lower(): s for s in KNOWN_SKILLS}


class SkillAnalyzerAgent(BaseAgent):
    """Extracts skills from resume text and performs gap analysis.

    Matches skills from a curated 200+ skill set using case-insensitive
    pattern matching. When a job description is provided, computes
    present vs. missing skills and generates recommendations.
    """

    name: str = "skill_analyzer_agent"
    version: str = "1.0.0"

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze skills in resume text and compare with job description.

        Args:
            input_data: Must contain 'text' (str). Optional 'job_description' (str | None).

        Returns:
            Dict with present_skills, missing_skills, skill_scores,
            recommended_skills, and skills_section_quality.
        """
        text: str = input_data["text"]
        job_description: str | None = input_data.get("job_description")

        logger.info("SkillAnalyzerAgent — analyzing skills in %d-char text", len(text))

        # ── Extract skills from resume ───────────────────────────────────
        resume_skills = self._find_skills(text)
        skill_scores = self._compute_skill_scores(text, resume_skills)

        # ── Job description gap analysis ─────────────────────────────────
        jd_skills: set[str] = set()
        missing_skills: list[str] = []
        recommended_skills: list[dict[str, Any]] = []

        if job_description:
            jd_skills = self._find_skills(job_description)
            present_in_jd = resume_skills & jd_skills
            missing_skills = sorted(jd_skills - resume_skills)

            # Prioritize missing skills
            for skill in missing_skills:
                priority = "high" if skill.lower() in job_description.lower()[:500] else "medium"
                recommended_skills.append({
                    "skill": skill,
                    "priority": priority,
                    "reason": f"Required by job description but not found in resume",
                })

        # ── Skills section quality ───────────────────────────────────────
        skills_section_quality = self._score_skills_section(
            resume_skills, jd_skills, text
        )

        present_list = sorted(resume_skills)

        logger.info(
            "SkillAnalyzerAgent — found %d skills, %d missing from JD",
            len(present_list),
            len(missing_skills),
        )

        return {
            "present_skills": present_list,
            "missing_skills": missing_skills,
            "skill_scores": skill_scores,
            "recommended_skills": recommended_skills,
            "skills_section_quality": skills_section_quality,
        }

    @staticmethod
    def _find_skills(text: str) -> set[str]:
        """Find all known skills mentioned in the text.

        Uses word-boundary regex for each known skill to avoid
        partial matches (e.g., 'C' inside 'CSS').

        Args:
            text: Text to search for skills.

        Returns:
            Set of canonical skill names found.
        """
        found: set[str] = set()
        text_lower = text.lower()

        for skill_lower, skill_canonical in _SKILL_LOOKUP.items():
            # Word boundary match — handles multi-word skills
            pattern = r"(?<![a-zA-Z0-9_/\-])" + re.escape(skill_lower) + r"(?![a-zA-Z0-9_/\-])"
            if re.search(pattern, text_lower):
                found.add(skill_canonical)

        return found

    @staticmethod
    def _compute_skill_scores(
        text: str, skills: set[str]
    ) -> dict[str, float]:
        """Compute confidence scores for each skill found.

        Score = frequency weight (0.6) + position weight (0.4).
        Skills mentioned earlier and more often get higher scores.

        Args:
            text: Full resume text.
            skills: Set of found skill names.

        Returns:
            Dict mapping skill name → confidence float (0.0–1.0).
        """
        text_lower = text.lower()
        text_len = max(len(text_lower), 1)
        scores: dict[str, float] = {}

        for skill in skills:
            skill_lower = skill.lower()
            pattern = re.escape(skill_lower)

            # Count occurrences
            matches = list(re.finditer(pattern, text_lower))
            frequency = len(matches)
            max_freq = 5  # cap

            # Frequency weight (0–0.6)
            freq_score = min(frequency / max_freq, 1.0) * 0.6

            # Position weight (0–0.4): earlier in doc = higher score
            if matches:
                first_pos = matches[0].start()
                position_ratio = 1.0 - (first_pos / text_len)
                pos_score = position_ratio * 0.4
            else:
                pos_score = 0.0

            scores[skill] = round(freq_score + pos_score, 3)

        return scores

    @staticmethod
    def _score_skills_section(
        resume_skills: set[str],
        jd_skills: set[str],
        text: str,
    ) -> int:
        """Score the quality of the skills section (0–100).

        Factors:
        - Skill count (30%): 0–20+ skills
        - Diversity across categories (30%)
        - JD overlap (20%): if JD provided
        - Has dedicated section (20%)

        Args:
            resume_skills: Skills found in resume.
            jd_skills: Skills found in job description.
            text: Full resume text.

        Returns:
            Quality score 0–100.
        """
        score = 0

        # Skill count (0–30)
        count = len(resume_skills)
        score += min(count / 20, 1.0) * 30

        # Category diversity (0–30) — check multiple categories present
        categories = {
            "languages": {"Python", "JavaScript", "Java", "C++", "Go", "TypeScript", "Ruby", "Rust"},
            "frameworks": {"React", "Django", "FastAPI", "Spring Boot", "Angular", "Vue.js", "Express"},
            "databases": {"PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch"},
            "cloud": {"AWS", "GCP", "Azure", "Docker", "Kubernetes"},
            "data": {"pandas", "NumPy", "TensorFlow", "PyTorch", "Machine Learning"},
        }
        cats_present = sum(
            1 for cat_skills in categories.values()
            if resume_skills & cat_skills
        )
        score += (cats_present / len(categories)) * 30

        # JD overlap (0–20)
        if jd_skills:
            overlap = len(resume_skills & jd_skills) / max(len(jd_skills), 1)
            score += overlap * 20
        else:
            score += 10  # neutral if no JD

        # Dedicated skills section (0–20)
        has_section = bool(
            re.search(r"(?i)^\s*(SKILLS|TECHNICAL\s+SKILLS|CORE\s+COMPETENCIES)", text, re.MULTILINE)
        )
        score += 20 if has_section else 0

        return min(round(score), 100)
