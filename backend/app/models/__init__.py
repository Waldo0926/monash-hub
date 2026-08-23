"""SQLAlchemy models.

Importing this package registers every table on ``Base.metadata`` which is what
Alembic autogenerate and the test fixtures rely on.
"""
from app.models.community import (  # noqa: F401
    CommunityAnswer,
    CommunityBookmark,
    CommunityPost,
    CommunityReport,
    CommunityTag,
    CommunityVote,
    PostTag,
)
from app.models.crawl import CrawlHistory, CrawlJob, SourceChangeEvent  # noqa: F401
from app.models.handbook import (  # noqa: F401
    Unit,
    UnitActivity,
    UnitAssessment,
    UnitLearningOutcome,
    UnitOffering,
    UnitRequisiteGroup,
    UnitRequisiteItem,
    UnitVersion,
)
from app.models.knowledge import (  # noqa: F401
    FaqEntry,
    OfficialPage,
    OfficialPageVersion,
    OfficialSource,
)
from app.models.translation import ContentTranslation  # noqa: F401
from app.models.user import (  # noqa: F401
    EmailVerificationCode,
    Notification,
    User,
)
