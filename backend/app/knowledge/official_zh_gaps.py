"""Chinese for the official-page sentences the machine pass could not translate.

The free chat model behind ``crawler.translate`` refused some sentences outright
(its content filter: a sexual-health glossary) and, for the rest, gave a
rendering that failed ``facts_kept`` - a dollar amount read as 澳元, a date or a
number changed, "I can't…" read as the model's own apology. Each pass sent them
again and stored nothing, so 234 sentences on 177 guides stayed in English
(audit of 2026-10-26).

These were drafted by AI and checked only against the English, the same
standing as ``structure_zh.py``: stored as *curated*, which beats the machine
but is not shown as a checked translation. Keyed on the exact English string
the page gives (``crawler.translate.run.page_strings``), per guide slug.
Numbers, amounts ($ stays $, RM stays RM), dates, codes, addresses and names
are copied as written; a source string the extractor cut short is translated
up to the same point.
"""
from __future__ import annotations

OFFICIAL_ZH_GAPS: dict[str, dict[str, str]] = {
    "2022-graduate": {
        "2022\n\nGraduate Certificate\n\n• B4004 - Graduate Certificate of Indigenous Business Leadership\n• B4005 - Graduate Certificate of Project Management\n• B4006 - Graduate Certificate of Business Management\n• B4007 - Graduate Certificate of Business Innovation\n• B4008 - Graduate Certificate of Analytics\n• B4009 - Graduate Certificate of Business Administration (Digital)\n• B4012 - Graduate Certificate of ":
            "2022\n\n研究生证书\n\n• B4004 - 原住民商业领导力研究生证书\n• B4005 - 项目管理研究生证书\n• B4006 - 商业管理研究生证书\n• B4007 - 商业创新研究生证书\n• B4008 - 分析学研究生证书\n• B4009 - 工商管理（数字化）研究生证书\n• B4012 - ……研究生证书",
    },
    "2022-undergraduate": {
        "2022\n\nBusiness and associated double degrees\n\n• B2000 - Bachelor of Business\n• B2017 - Bachelor of Business and Bachelor of Information Technology\n• B2019 - Bachelor of Business and Bachelor of Arts\n• B2028 - Bachelor of Business and Bachelor of Media Communication\n• B2035 - Bachelor of Business and Bachelor of Banking and Finance\n• B2037 - Bachelor of Business and Bachelor of Marketing\n• B2040 - ":
            "2022\n\n商学及相关双学位\n\n• B2000 - 商学学士\n• B2017 - 商学学士和信息技术学士\n• B2019 - 商学学士和文学学士\n• B2028 - 商学学士和媒体传播学士\n• B2035 - 商学学士和银行与金融学士\n• B2037 - 商学学士和市场营销学士\n• B2040 - ",
    },
    "2024-undergraduate": {
        "2024\n\nBusiness and associated double degrees\n\n• B2000 – Bachelor of Business\n• B2017 – Bachelor of Business and Bachelor of Information Technology\n• B2019 – Bachelor of Business and Bachelor of Arts\n• B2028 – Bachelor of Business and Bachelor of Media Communication\n• B2035 – Bachelor of Business and Bachelor of Banking and Finance\n• B2037 – Bachelor of Business and Bachelor of Marketing\n• B2040 – ":
            "2024\n\n商学及相关双学位\n\n• B2000 – 商学学士\n• B2017 – 商学学士和信息技术学士\n• B2019 – 商学学士和文学学士\n• B2028 – 商学学士和媒体传播学士\n• B2035 – 商学学士和银行与金融学士\n• B2037 – 商学学士和市场营销学士\n• B2040 – ",
    },
    "2025-undergraduate": {
        "2025\n\nBusiness and associated double degrees\n\n• B2000 – Bachelor of Business\n• B2017 – Bachelor of Business and Bachelor of Information Technology\n• B2019 – Bachelor of Business and Bachelor of Arts\n• B2028 – Bachelor of Business and Bachelor of Media Communication\n• B2035 – Bachelor of Business and Bachelor of Banking and Finance\n• B2037 – Bachelor of Business and Bachelor of Marketing\n• B2040 – ":
            "2025\n\n商学及相关双学位\n\n• B2000 – 商学学士\n• B2017 – 商学学士和信息技术学士\n• B2019 – 商学学士和文学学士\n• B2028 – 商学学士和媒体传播学士\n• B2035 – 商学学士和银行与金融学士\n• B2037 – 商学学士和市场营销学士\n• B2040 – ",
    },
    "2026-undergraduate": {
        "Course progression maps for 2026 commencing students\n\nBusiness and associated double degrees\n\n• B2000 – Bachelor of Business\n• B2017 – Bachelor of Business and Bachelor of Information Technology\n• B2019 – Bachelor of Business and Bachelor of Arts\n• B2028 – Bachelor of Business and Bachelor of Media Communication\n• B2035 – Bachelor of Business and Bachelor of Banking and Finance\n• B2037 – Bachelor ":
            "2026 年入学学生的学位课程进度规划图\n\n商学及相关双学位\n\n• B2000 – 商学学士\n• B2017 – 商学学士和信息技术学士\n• B2019 – 商学学士和文学学士\n• B2028 – 商学学士和媒体传播学士\n• B2035 – 商学学士和银行与金融学士\n• B2037 – 学士",
    },
    "2027-undergraduate": {
        "Course progression maps for 2027 commencing students\n\nBusiness and associated double degrees\n\n• B2000 – Bachelor of Business\n• B2017 – Bachelor of Business and Bachelor of Information Technology\n• B2019 – Bachelor of Business and Bachelor of Arts\n• B2028 – Bachelor of Business and Bachelor of Media Communication\n• B2035 – Bachelor of Business and Bachelor of Banking and Finance\n• B2037 – Bachelor ":
            "2027 年入学学生的学位课程进度规划图\n\n商学及相关双学位\n\n• B2000 – 商学学士\n• B2017 – 商学学士和信息技术学士\n• B2019 – 商学学士和文学学士\n• B2028 – 商学学士和媒体传播学士\n• B2035 – 商学学士和银行与金融学士\n• B2037 – 学士",
    },
    "academic-progress-receiving-notice": {
        "You may also provide supporting documentation. If your supporting documentation isn’t available by the due date, let the faculty know when you’ll be able to provide it before the specified deadline.":
            "你也可以提交证明材料。如果你的证明材料在截止日期前还没有准备好，请告知学院你能在规定期限之前的什么时候提交。",
    },
    "accommodation-housing": {
        "This is an incredible organisation that provides support to many vulnerable women. If you’re interested in donating to them visit the website. All donations above $2 are tax deductible.":
            "这是一个了不起的机构，为许多处境弱势的女性提供支持。如果你有意向她们捐款，请访问其网站。所有 $2 以上的捐款均可抵税。",
    },
    "after-arrival-shopping-transport": {
        "The final total price of your purchase (if paying by cash) is rounded down or up to the nearest five cents. This means, for example, you won’t get change if you pay $10 for a $9.98 item.":
            "你购物的最终总价（如以现金支付）会向下或向上取整到最接近的五分钱。例如，这意味着如果你用 $10 购买一件 $9.98 的商品，将不会找零。",
        "payWave or PayPass where you just tap your credit or debit card on a device to make a payment up to $100 without entering a PIN and more if you enter a PIN":
            "payWave 或 PayPass：只需将信用卡或借记卡在设备上轻触一下即可付款，$100 以内无需输入 PIN，输入 PIN 则可支付更高金额",
    },
    "after-you-apply-withdrawal-policy-for-semester-exc": {
        "If you wish to withdraw your participation in a Semester Abroad program, which includes Exchange, Independent Study Abroad (ISA) and the Semester in Australia (SIA) or Malaysia (SIM) Programs, formerly the Global Intercampus Program (GIP), it is really important that you notify Monash Abroad as soon as you can.":
            "如果你想退出 Semester Abroad（海外学期）项目——包括交换（Exchange）、独立海外学习（Independent Study Abroad，ISA）以及澳大利亚学期（Semester in Australia，SIA）或马来西亚学期（Semester in Malaysia，SIM）项目（前身为 Global Intercampus Program，GIP）——务必尽快通知 Monash Abroad（海外学习与交换）。",
    },
    "amenities-2026": {
        "The maximum amount charged to any student enrolled in 2026 is $373 and may be less, depending on your enrolment load.":
            "2026 年入学的学生最多需缴纳 $373，实际金额可能更低，取决于你的选课量。",
    },
    "apply-online": {
        "$125 applicant fee (or a waiver code)":
            "$125 申请费（或减免代码）",
        "International applicants need to pay a $125 application fee and attach proof of payment. For payment options, see application fee payments.":
            "国际申请人需缴纳 $125 申请费并附上付款证明。付款方式请参阅申请费缴纳说明。",
    },
    "aquila-advisers": {
        "Hi guys! I’m Alex, a third-year Occupational Therapy student. Outside of being an adviser, I’m passionate about pushing my personal best in marathons and hitting the gym. I also enjoy singing – especially Cantopop – and I’ll never say no to a karaoke session! As an adviser, I’m excited to meet new people, build strong connections and help create a fun, relaxed space through MSC events. Looking forward to an amazing year together.":
            "大家好！我是 Alex，作业治疗专业三年级学生。除了担任宿舍导师（adviser）之外，我热衷于在马拉松中不断刷新个人最好成绩，也喜欢去健身房。我还喜欢唱歌——尤其是粤语流行歌——K 歌邀约我从不拒绝！作为导师，我很期待结识新朋友、建立紧密的联系，并通过 MSC 活动一起营造轻松有趣的氛围。期待和大家共度精彩的一年。",
        "Hi there, I'm Alan. I’m an international student hailing from the vibrant city of Hong Kong. I'm currently pursuing my bachelors degree in Occupational Therapy, and I'm thrilled to be part of the adviser team at Aquila. Beyond my academic pursuits, I find joy in spending time with friends, playing the piano, and belting out my favourite tunes at karaoke nights. Feel free to reach out to me! Let's make the most of our time at Aquila and create lasting memories together. Looking forward to meeting you all!":
            "你好，我是 Alan，一名来自活力之城香港的国际学生。我目前正在攻读作业治疗学士学位，很高兴能加入 Aquila 的宿舍导师（adviser）团队。学业之外，我喜欢和朋友们待在一起、弹钢琴，还喜欢在 K 歌之夜放声高唱我最爱的歌曲。欢迎随时联系我！让我们在 Aquila 好好把握时光，一起创造难忘的回忆。期待与大家见面！",
    },
    "arts-postgraduate-by-coursework-pgcw-and-honours-o": {
        "Monash Abroad to notify you of final approval and pay Monash Abroad Travel Scholarship ($200) and Monash University Travel Insurance.":
            "由 Monash Abroad（海外学习与交换）通知你最终审批结果，并发放 Monash Abroad 旅行奖学金（$200）、支付 Monash University 旅行保险。",
    },
    "assets-college-adviser-listing": {
        "Hi guys! I’m Alex, a third-year Occupational Therapy student. Outside of being an adviser, I’m passionate about pushing my personal best in marathons and hitting the gym. I also enjoy singing – especially Cantopop – and I’ll never say no to a karaoke session! As an adviser, I’m excited to meet new people, build strong connections and help create a fun, relaxed space through MSC events. Looking forward to an amazing year together.":
            "大家好！我是 Alex，作业治疗专业三年级学生。除了担任宿舍导师（adviser）之外，我热衷于在马拉松中不断刷新个人最好成绩，也喜欢去健身房。我还喜欢唱歌——尤其是粤语流行歌——K 歌邀约我从不拒绝！作为导师，我很期待结识新朋友、建立紧密的联系，并通过 MSC 活动一起营造轻松有趣的氛围。期待和大家共度精彩的一年。",
        "Hi there, I'm Alan. I’m an international student hailing from the vibrant city of Hong Kong. I'm currently pursuing my bachelors degree in Occupational Therapy, and I'm thrilled to be part of the adviser team at Aquila. Beyond my academic pursuits, I find joy in spending time with friends, playing the piano, and belting out my favourite tunes at karaoke nights. Feel free to reach out to me! Let's make the most of our time at Aquila and create lasting memories together. Looking forward to meeting you all!":
            "你好，我是 Alan，一名来自活力之城香港的国际学生。我目前正在攻读作业治疗学士学位，很高兴能加入 Aquila 的宿舍导师（adviser）团队。学业之外，我喜欢和朋友们待在一起、弹钢琴，还喜欢在 K 歌之夜放声高唱我最爱的歌曲。欢迎随时联系我！让我们在 Aquila 好好把握时光，一起创造难忘的回忆。期待与大家见面！",
        "Hi, I am Aditi Mehta, I'm pursuing Master of Cyber Security. I like binge-watching TV shows and movies Shrinking being my fav at the moment), chilling at the beach reading a book, and going on small hikes. I am also passionate about food, I would not be able to pick just one meal to eat for the rest of my life. Looking forward to meeting you all and making new friends!!":
            "大家好，我是 Aditi Mehta，正在攻读网络安全硕士。我喜欢刷剧和看电影（目前最爱的是《Shrinking》），喜欢在海滩边放松看书，也喜欢短途徒步。我还热爱美食，要我余生只吃一道菜，我实在选不出来。期待与大家见面，结交新朋友！！",
    },
    "australia-awards-forms": {
        "reimbursement claim form (pdf, 0.16 mb).":
            "报销申请表（pdf，0.16 mb）。",
    },
    "before-leaving-home-country-sessions": {
        "You’ll hear from Monash staff and current students about what to expect when you arrive and in your first few weeks, and how to make the most of your new life in Australia. While we can’t provide course-specific advice, we’ll cover the essentials to help you feel confident and ready for the journey ahead.":
            "你将听到 Monash 的工作人员和在校学生介绍抵达时以及最初几周会遇到的情况，以及如何充分享受你在澳大利亚的新生活。我们不针对具体学位课程提供建议，但会讲解各项必备信息，帮助你自信从容地开启接下来的旅程。",
    },
    "business-course-maps": {
        "2027\n\nUndergraduate\n\nGraduate\n\nCourse progression maps for 2027 commencing students\n\nBusiness and associated double degrees\n\n• B2000 – Bachelor of Business\n• B2017 – Bachelor of Business and Bachelor of Information Technology\n• B2019 – Bachelor of Business and Bachelor of Arts\n• B2028 – Bachelor of Business and Bachelor of Media Communication\n• B2035 – Bachelor of Business and Bachelor of Banking ":
            "2027\n\n本科\n\n研究生\n\n2027 年入学学生的学位课程进度规划图\n\n商学及相关双学位\n\n• B2000 – 商学学士\n• B2017 – 商学学士和信息技术学士\n• B2019 – 商学学士和文学学士\n• B2028 – 商学学士和媒体传播学士\n• B2035 – 商学学士和银行",
    },
    "business-scholarships-sponsorships-and-awards": {
        "The awardee will receive a trophy and a prize of $500 or equivalent at an international campus.":
            "获奖者将获得一座奖杯及 $500 奖金（在国际校区则为等值奖金）。",
    },
    "campus-life-lost-and-found-property": {
        "You might be liable to pay a minimum of $150 if you don't find the item.":
            "如果你找不到该物品，可能需要支付至少 $150。",
    },
    "card-single-load-terms-and-conditions": {
        "If you lose the Card, a $9.95 fee is charged to issue a replacement. The fee is deducted from the balance on your card.":
            "如果你遗失了该卡，补办需收取 $9.95 的费用，该费用将从卡内余额中扣除。",
    },
    "careers-jobs-board": {
        "James N Stevens Summer Scholarship\n\nDuration: Two weeks\n \n \nApplications close: 4 Nov 2026\n\nEach year, Maroondah City Council offers a scholarship in recognition of the many years of valuable service given to the local community by the former Deputy Town Clerk of the City of Croydon, the late Mr James (Jim) Stevens. The Scholarship is valued at $3,000 and will be completed between November 2026 and February 2027, at a mutually convenient time.\nMaroondah City Council":
            "James N Stevens 夏季奖学金\n\n时长：两周\n \n \n申请截止：2026年11月4日\n\nMaroondah City Council（马隆达市议会）每年提供一项奖学金，以表彰已故的 James（Jim）Stevens 先生——前 Croydon 市副镇书记——多年来为当地社区作出的宝贵贡献。该奖学金价值 $3,000，将于 2026年11月至2027年2月期间、在双方都方便的时间完成。\nMaroondah City Council（马隆达市议会）",
    },
    "caulfield-program-cost": {
        "Deposit payment: $100. Payment details will be provided to successful applicants.":
            "押金：$100。付款详情将提供给成功入选的申请人。",
    },
    "cle--our-history": {
        "The Monash Legal Service (as it was then known) first began offering legal advice to Monash University students in a room in the Law School Building during the 1970s. In 1975, the Faculty of Law launched the ‘Professional Practice’ unit at the Springvale Legal Service which meant that students could now receive academic credit towards their degree for a semester of working at the service under supervision of lawyer mentor/supervisors. In 1979, under the name “Monash-Oakleigh Legal Service” the service began to accept students enrolled in the new 'Professional Practice' unit, and opened up its ":
            "Monash Legal Service（当时的名称）最早于 20 世纪 70 年代在法学院大楼的一间房间里开始为 Monash University 学生提供法律咨询。1975 年，法学院在 Springvale Legal Service 推出了“Professional Practice（专业实践）”课程，这意味着学生在律师导师/督导的指导下在该服务机构工作一个学期，即可获得计入学位的学分。1979 年，该服务以“Monash-Oakleigh Legal Service”之名开始接收选修新开设的“Professional Practice”课程的学生，并开放了其",
    },
    "clinical-legal-education-clinical-placement-offeri": {
        "As a placement student , you will review pleadings in matters valued at $150,000 or less (including any counterclaim) to assist in identifying cases suitable for arbitration. These matters form a key focus of the Court’s early arbitration pathway. Working closely with the Judge in Charge of the Arbitration List, you will prepare briefings to support judicial consideration and referral of appropriate cases to arbitration.":
            "作为实习学生，你将审阅涉案金额在 $150,000 或以下（含任何反诉）的案件诉状，协助识别适合仲裁的案件。这类案件是法院早期仲裁途径的重点。你将与仲裁案件表主审法官（Judge in Charge of the Arbitration List）密切合作，撰写简报，以支持法官审议案件并将合适的案件转交仲裁。",
        "Lawyer Assisted Family Dispute Resolution (LAFDR) sessions are conducted by experienced FDRPs from Sunshine Family Relationship Centre and other Family Relationship Centres.":
            "律师协助家庭纠纷调解（Lawyer Assisted Family Dispute Resolution，LAFDR）会议由来自 Sunshine Family Relationship Centre 及其他家庭关系中心（Family Relationship Centres）的资深家庭纠纷调解员（FDRP）主持。",
    },
    "connect-letters": {
        "You can check the progress of your order in WES. \n\nCost: $45 each":
            "你可以在 WES（学生系统）中查看订单进度。 \n\n费用：每份 $45",
    },
    "connect-qualifications": {
        "Request a Qualification Confirmation. This information is confidential, so you’ll need written consent from the graduate. Cost: $39":
            "申请学历确认（Qualification Confirmation）。此信息属于保密信息，因此你需要获得毕业生的书面同意。费用：$39",
        "request an Enrolment Status or Qualification Confirmation. This information is confidential, so you’ll need written consent from the graduate. Cost: $39.":
            "申请在读状态证明（Enrolment Status）或学历确认（Qualification Confirmation）。此信息属于保密信息，因此你需要获得毕业生的书面同意。费用：$39。",
    },
    "continuous-professional-development-work-experienc": {
        "Some resources that will help you understand your rights when engaging in work experience are below:":
            "以下资源可以帮助你了解参加工作实习时享有的权利：",
    },
    "dates-holidays": {
        "University holidays 2026\n\nUniversity holidays 2022\nHoliday | Date\n2026 New Year's Day | Thursday 1 January\nUniversity closed | Friday 2 January\nUniversity reopens | Monday 5 January\nPublic holiday | Monday 26 January\nGood Friday | Friday 3 April\nEaster Saturday | Saturday 4 April\nEaster Sunday | Sunday 5 April\nEaster Monday | Monday 6 April\nEaster Tuesday (University only) | Tuesday 7 April\nAnzac ":
            "2026 年大学假期\n\n2022 年大学假期\n假期 | 日期\n2026 年元旦 | 1月1日星期四\n大学关闭 | 1月2日星期五\n大学重新开放 | 1月5日星期一\n公共假期 | 1月26日星期一\n耶稣受难日 | 4月3日星期五\n复活节星期六 | 4月4日星期六\n复活节星期日 | 4月5日星期日\n复活节星期一 | 4月6日星期一\n复活节星期二（仅限大学） | 4月7日星期二\n澳新军团（Anzac）",
    },
    "dental-appointments": {
        "Make sure you only book an appointment if you can attend it – booking appointments you can’t attend could prevent someone else from getting urgent dental care. A $30 fee applies for late cancellations (within three hours of the appointment time) and no-shows.":
            "请只在确定能赴约时才预约——预约了却无法到场，可能会让其他人得不到紧急牙科治疗。迟取消（预约时间前三小时内）和爽约将收取 $30 费用。",
    },
    "during-study-australian-culture": {
        "If you’ve accepted an invitation and later find you can’t attend, it’s good manners to let the person who invited you know. Or, if you want to decline an invitation, it’s considered polite to say so (e.g. ‘Thank you, but unfortunately I can’t join you’).":
            "如果你已接受邀请，之后发现去不了，礼貌的做法是告知邀请你的人。或者，如果你想婉拒邀请，直接说明也被视为得体的做法（例如：“谢谢，不过很遗憾这次我去不了”）。",
    },
    "during-study-healthcare-australia": {
        "You may need to pay an upfront fee between $400 and $700 before being treated. You can call your Overseas Student Health Cover (OSHC) provider to ask if they might offer a hospital guarantee so you don’t have to pay upfront. If you can’t get a guarantee, you can later submit a claim to your OSHC provider for possible reimbursement.":
            "你可能需要在接受治疗前预先支付 $400 至 $700 的费用。你可以致电你的 OSHC（留学生医疗保险）提供商，询问他们能否提供医院担保（hospital guarantee），这样你就不必预先付款。如果拿不到担保，你之后可以向 OSHC 提供商提交理赔申请，争取报销。",
    },
    "employability-skills-social-impact-hackathon-serie": {
        "Receive $2,000 in prize money (shared among team members).":
            "获得 $2,000 奖金（由团队成员共享）。",
    },
    "engineering-student-industry-engagement": {
        "Gain Real-World Experience with an IIPGain hands-on experience and a competitive edge for your career. Apply your skills to real industry challenges, building your professional network, and enhancing your employability—all while earning an industry-funded scholarship.":
            "通过 IIP 获得真实工作经验通过实践积累经验，为你的职业发展赢得竞争优势。将你的技能应用于真实的行业挑战，拓展职业人脉，提升就业竞争力——同时还能获得由行业资助的奖学金。",
    },
    "entry-requirements-atar": {
        "the course is new and a lowest selection rank isn’t available from the previous year":
            "该学位课程为新开设课程，没有上一年的最低录取排名（lowest selection rank）",
    },
    "equity-diversity-inclusion-workshops-training": {
        "Rainbow Communities and LGBTIQA+ 101\n \n\nIf you’d like to learn more about sex, gender and sexuality, then this module is for you! Starting with the basics, this course will help you build foundational knowledge of LGBTIQA+ terms, identities, and communities, and empower you to continue your allyship journey.":
            "彩虹社群与 LGBTIQA+ 101（入门）\n \n\n如果你想进一步了解生理性别、社会性别与性取向，这个模块就是为你准备的！本课程从基础讲起，帮助你建立对 LGBTIQA+ 相关术语、身份认同和社群的基础认识，并助你在成为盟友（ally）的道路上继续前行。",
    },
    "exams-troubleshooting": {
        "I can’t share my microphone":
            "无法共享麦克风",
        "I can’t share my screen":
            "无法共享屏幕",
        "I can’t share my webcam":
            "无法共享摄像头",
    },
    "exchange-faq": {
        "What if I can’t enrol in my approved units?":
            "如果选不上已获批准的课程怎么办？",
    },
    "exclusion-appeal": {
        "If any relevant documents aren’t available when you submit the appeal form, we may be able to include them in the appeal later on – just make sure you mention this in the appeal form.":
            "如果你提交申诉表时某些相关文件还没有准备好，我们之后或许可以将其补充到申诉中——只需确保在申诉表中注明这一点。",
    },
    "financial-assistance-card": {
        "Click the activation link in the email (subject line: Your $50 prepaid student card is here) – you’ll be taken to the Activate Prepaid Student Card screen.":
            "点击邮件（主题：Your $50 prepaid student card is here）中的激活链接——你将进入 Activate Prepaid Student Card（激活预付学生卡）页面。",
        "To make everyday campus life a little more affordable, eligible students were given up to $50 on a prepaid student card to spend on food, drinks and essentials at participating retailers.":
            "为了让日常校园生活更实惠一些，符合条件的学生获得了最高 $50 的预付学生卡额度，可在参与活动的商家购买餐饮和生活必需品。",
        "Your card was loaded with $25 on 13 April, with a further $25 automatically added on 20 April.":
            "你的卡已于 4月13日充值 $25，并于 4月20日自动再充值 $25。",
    },
    "financial-assistance-placements": {
        "$331.65 per week (from 1 July to 28 December 2025), and":
            "每周 $331.65（2025年7月1日至12月28日），以及",
        "If exceptional circumstances prevent you from meeting the income criteria, you’ll need to show that you’d usually meet the criteria during your normal studies (for example, you worked a minimum of 15 hours and earned less than $1,500 (for 2025 placements) or $1,536.37 (for 2026 placements) a week prior to being impacted by exceptional circumstances).":
            "如果特殊情况导致你达不到收入标准，你需要证明在正常学习期间你通常能够满足该标准（例如，在受到特殊情况影响之前，你每周工作至少 15 小时，且每周收入低于 $1,500（适用于 2025 年的实习）或 $1,536.37（适用于 2026 年的实习））。",
        "earned no more than $1,500 per week during 2025 or $1,536.70 per week during 2026 (before tax) on average within the same four-week period. This includes scholarship payments, or similar financial cost-of-living assistance from the Commonwealth, States and Territories.":
            "在同一四周期间内，平均每周收入（税前）不超过 $1,500（2025 年）或 $1,536.70（2026 年）。这包括奖学金，或来自联邦、州和领地政府的类似生活费资助。",
    },
    "financial-information-new-colombo-plan-mobility-pr": {
        "A limited number of grants up to $6,000 each are available to Monash University students for a selection of undergraduate Global Study Tours and Language Intensive Programs. These grants are awarded on the basis of the number of available grants.":
            "Monash University 学生可申请数量有限、每笔最高 $6,000 的资助，用于部分本科 Global Study Tours（海外游学）及 Language Intensive Programs（语言强化项目）。这些资助根据可提供的名额发放。",
    },
    "financial-information-new-colombo-plan-semester-pr": {
        "A limited number of grants up to $15,000 each are available to Monash University students for study in a specific field of study in Indo-Pacific countries at selected exchange partners. If the number of available grants is less than the number of eligible students, students are selected on evaluation of their personal statement (if this was part of the program selection), on academic merit (the WAM in the student’s current degree at the time of being accepted into the program) and equity indicators..":
            "Monash University 学生可申请数量有限、每笔最高 $15,000 的资助，用于在印太地区国家的指定交换合作院校学习特定学科领域。如果可提供的资助名额少于符合条件的学生人数，将根据学生的个人陈述（如果项目选拔包含此项）、学业成绩（即学生被项目录取时当前学位的 WAM（加权平均分））以及公平指标进行选拔。",
    },
    "global-summer-and-winter-programs-further-informat": {
        "Monash Abroad will email you the outcome of your application directly to your student email account. Please do not contact us for updates during this time and we will not be able to provide them.":
            "Monash Abroad（海外学习与交换）会将申请结果直接发送到你的学生邮箱。在此期间请勿联系我们询问进展，我们也不会提供进展更新。",
    },
    "government-support-hecs-help": {
        "10% discount (payments of $500 or more)":
            "10% 折扣（付款 $500 或以上）",
        "From 1 January 2023, you'll no longer receive a 10% discount when you make an upfront payment of $500 or more on your HECS-HELP loan. However, you’ll still be able to receive the HECS-HELP up-front discount for any unit with a census date in 2021 or 2022.":
            "自 2023年1月1日起，你为 HECS-HELP 贷款一次性预付 $500 或以上时，将不再享受 10% 折扣。不过，对于 census date（学籍统计日）在 2021 年或 2022 年的任何课程，你仍可享受 HECS-HELP 预付折扣。",
        "From 1 January 2023, you’ll no longer receive a 10% discount when you make an upfront payment of $500 or more on your HECS-HELP loan. However, you’ll still be able to receive the HECS-HELP up-front discount for any unit with a census date in 2021 or 2022.":
            "自 2023年1月1日起，你为 HECS-HELP 贷款一次性预付 $500 或以上时，将不再享受 10% 折扣。不过，对于 census date（学籍统计日）在 2021 年或 2022 年的任何课程，你仍可享受 HECS-HELP 预付折扣。",
    },
    "graduate-research-examination": {
        "MADA offers up to $900 in exhibition support funding. All requested reimbursements must comply with the Monash reimbursement policy. To request reimbursement for eligible expenses, please fill in the MADA HDR Support Scheme form.":
            "MADA 提供最高 $900 的展览资助。所有报销申请必须符合 Monash 报销政策。如需申请报销符合条件的费用，请填写 MADA HDR Support Scheme（HDR 支持计划）表格。",
    },
    "graduate-research-funding": {
        "$1,500 after successful completion of the Progress Review":
            "顺利完成 Progress Review（进度评审）后获得 $1,500",
        "$2,000 after successful Confirmation of candidature":
            "顺利通过 Confirmation of candidature（候选资格确认）后获得 $2,000",
        "$2,500 after successful Confirmation of candidature":
            "顺利通过 Confirmation of candidature（候选资格确认）后获得 $2,500",
        "Master students - $2,000 for the duration of candidature (i.e. up to 2 years full-time equivalent). Students will receive:":
            "硕士研究生 - 在整个候选期内（即最多相当于 2 年全日制）可获得 $2,000。学生将获得：",
        "PhD students  - $4,000 for the duration of candidature (i.e. up to 4 years full-time equivalent). Students will receive:":
            "博士生  - 整个候选期内（即最长相当于 4 年全日制）共 $4,000。学生将获得：",
    },
    "graduate-research-key-resources": {
        "Please note: From January 2024, the completion of the online Human Research Ethics module available through myDevelopment is mandatory for all HDRs undertaking human research activities and who want to submit an ethics application for review to the Monash University Human Research Ethics Committee. The appreciation and compliance of ethical principles in research is also part of the academic research integrity module in professional development and can be found here.":
            "请注意：自 2024 年 1 月起，所有开展人类研究活动、并希望向 Monash University 人类研究伦理委员会提交伦理审查申请的 HDR 学生，都必须完成 myDevelopment 上的在线人类研究伦理模块。理解并遵守研究伦理原则也是专业发展中学术研究诚信模块的内容之一，可在此处找到。",
    },
    "graduate-research-summer-research-program-scholars": {
        "Participants will receive a scholarship of $600 per week. Students located interstate will be offered a travel allowance to cover return travel to Melbourne.":
            "参与者每周可获得 $600 的奖学金。居住在其他州的学生将获得一笔差旅补贴，用于支付往返墨尔本的交通费用。",
    },
    "graduate-research-travel-and-reimbursements": {
        "$1,000 towards costs incurred during candidature":
            "$1,000，用于支付候选期内产生的费用",
    },
    "graduate-semester-1-units": {
        "ACX4040 Issues in accounting information systems S1 Caulfield 16/03/2021 - 25/05/2021 Final assessment 25/05/2021 30/03/2021 31/03/2021 28/042021 24/05/2021":
            "ACX4040 会计信息系统专题 S1 Caulfield 16/03/2021 - 25/05/2021 期末考核 25/05/2021 30/03/2021 31/03/2021 28/042021 24/05/2021",
    },
    "guides-ceremony-australia": {
        "You can buy a copy in DVD, Blu-ray or USB format for $25 – place an order online before or after the ceremony.":
            "你可以购买 DVD、蓝光或 USB 格式的典礼录像，价格为 $25——可在典礼前或典礼后在线下单。",
    },
    "hearings-before-the-hearing": {
        "It’s a good idea to bring supporting evidence with you to the hearing (but you need to submit this to the committee ahead of time). You can submit documentary evidence up to two working days before the hearing. If your documentation is not available by that date, you can request permission to submit further evidence at the hearing.":
            "建议你在听证会时带上支持性证据（但你需要提前把这些证据提交给委员会）。你最晚可以在听证会前两个工作日提交书面证据。如果你的文件到那时还无法准备好，可以申请在听证会上提交补充证据。",
    },
    "how-it-works-tab-content-tab-1": {
        "Click the activation link in the email (subject line: Your $50 prepaid student card is here) – you’ll be taken to the Activate Prepaid Student Card screen.":
            "点击邮件（主题：Your $50 prepaid student card is here）中的激活链接——你将进入 Activate Prepaid Student Card（激活预付学生卡）页面。",
    },
    "industry-experience-graduate-industry-experience": {
        "Some resources that will help you understand your rights when engaging in work experience are below:":
            "以下资源可以帮助你了解参加工作实习时享有的权利：",
    },
    "industry-experience-undergraduate-industry-experie": {
        "Some resources that will help you understand your rights when engaging in work experience are below:":
            "以下资源可以帮助你了解参加工作实习时享有的权利：",
    },
    "jd-juris-doctor-law-degree-changes": {
        "I’d prefer to complete the new structure of the degree, why can’t I change? \nThe updated degree structure is designed for students who are just beginning their studies. Because you’ve already commenced your course, you’re enrolled in the current version of the degree, and your completed units map to that structure. Continuing in the course you started is the best and most efficient pathway to finishing your degree on time.":
            "我更想按新的学位结构完成学业，为什么不能更换？\n更新后的学位结构是为刚开始学习的学生设计的。由于你已经开始修读你的学位课程，你注册的是该学位的现行版本，你已完成的课程也对应这一结构。继续修读你已开始的学位课程，是按时完成学位最好、最高效的途径。",
    },
    "jd-monash-jd-oxford-pathway": {
        "The Oxford pathway is currently supported by the Nick Auden International Study Scholarship. This Scholarship will support Monash Law students to undertake one of the three international pathway programs established by the Monash Law Faculty. Please note, availability of this scholarship is dependent on funding at the time and there may be multiple awardees for amounts up to $10,000.":
            "牛津项目目前由 Nick Auden 国际留学奖学金（Nick Auden International Study Scholarship）资助。该奖学金将资助 Monash 法学院学生参加 Monash 法学院设立的三个国际项目之一。请注意，该奖学金能否提供取决于当时的资金情况，并且可能有多名获奖者，每人金额最高 $10,000。",
    },
    "leadership-ancora-imparo": {
        "Receive a Certificate of Completion and a $500 stipend, while gaining recognition as part of one of Monash’s flagship leadership programs.":
            "获得结业证书（Certificate of Completion）和 $500 津贴，同时作为 Monash 旗舰领导力项目之一的成员获得认可。",
    },
    "leadership-betty-amsden": {
        "Mentors and mentees are expected to meet face-to-face, four to six times over the course of the mentoring relationship.":
            "在整个导师指导期间，导师和学员应面对面会面四到六次。",
        "The Betty Amsden Foundation is committed to funding this program. Each year, 18 scholarships valued at $6000 will be offered to students in the program.":
            "Betty Amsden 基金会致力于资助这一项目。每年将向项目中的学生提供 18 份奖学金，每份价值 $6000。",
        "provides a scholarship valued at $6,000.":
            "提供一份价值 $6,000 的奖学金。",
    },
    "level-one-units-chemistry": {
        "Unit code | Unit title | Semester | Campus | Mode | Prerequisites/\nadditional information | How to enrol\nCHM1011 | Chemistry 1 | 1 | Clayton | On-campus | No prerequisites\nProhibition: CHM1051 | Web enrolment system\nCHM1022 | Chemistry 2 | 2 | Clayton | On-campus | No prerequisites\nProhibition: CHM1052 | Web enrolment system\nCHM1051 | Chemistry 1 advanced | 1 | Clayton | On-campus | VCE Chemistry ":
            "课程代码 | 课程名称 | 学期 | 校区 | 授课方式 | 先修课程/\n其他信息 | 注册方式\nCHM1011 | 化学 1 | 1 | Clayton | 校内授课 | 无先修课程\n互斥课程：CHM1051 | 网上选课系统（WES）\nCHM1022 | 化学 2 | 2 | Clayton | 校内授课 | 无先修课程\n互斥课程：CHM1052 | 网上选课系统（WES）\nCHM1051 | 化学 1（高级） | 1 | Clayton | 校内授课 | VCE 化学 ",
    },
    "level-one-units-earth--atmosphere-and-environment": {
        "Unit code | Unit title | Semester | Campus | Mode | Prerequisites/\nadditional information | How to enrol\nCLI1100 | Climate change: A wicked problem | 1 | Clayton | On-campus | No prerequisites | Web enrolment system\nCLI1200 | Climate change: Impacts and adaptations | 2 | Clayton | On-campus | No prerequisites | Web enrolment system\nEAE1011 | The Earth system: From the core to the atmosphere | 1 | ":
            "课程代码 | 课程名称 | 学期 | 校区 | 授课方式 | 先修课程/\n其他信息 | 注册方式\nCLI1100 | 气候变化：一个棘手难题 | 1 | Clayton | 校内授课 | 无先修课程 | 网上选课系统（WES）\nCLI1200 | 气候变化：影响与适应 | 2 | Clayton | 校内授课 | 无先修课程 | 网上选课系统（WES）\nEAE1011 | 地球系统：从地核到大气层 | 1 | ",
    },
    "level-one-units-science-core-units": {
        "Unit code | Unit title | Semester | Campus | Mode | Prerequisites/\nadditional information | How to enrol\nADS1001 | Data challenges 1 | 1 | Clayton | On-campus | This unit is only available to students who are enrolled in S2010 Bachelor of Applied Data Science or S3003 Bachelor of Applied Data Science Advanced (Honours) | Web enrolment system\nADS1002 | Data challenges 2 | 2 | Clayton | On-campus | ":
            "课程代码 | 课程名称 | 学期 | 校区 | 授课方式 | 先修课程/\n其他信息 | 注册方式\nADS1001 | 数据挑战 1 | 1 | Clayton | 校内授课 | 本课程仅向注册 S2010 应用数据科学学士（Bachelor of Applied Data Science）或 S3003 应用数据科学高级（荣誉）学士（Bachelor of Applied Data Science Advanced (Honours)）的学生开放 | 网上选课系统（WES）\nADS1002 | 数据挑战 2 | 2 | Clayton | 校内授课 | ",
    },
    "m-pass-terms": {
        "A monthly administration fee of $5 will be charged to all inactive M-Pass accounts that have credit. “Inactive” means that you have not loaded any new value onto your M-Pass account or used your M-Pass account for 12 months.":
            "所有有余额的非活跃 M-Pass 账户每月将被收取 $5 的管理费。“非活跃”是指你在 12 个月内既没有向 M-Pass 账户充值，也没有使用过 M-Pass 账户。",
        "Refunds can only be given for amounts over $25 and only for the entire remaining balance in your M-Pass account. A $25 administration fee will be deducted from your balance when you request a refund. Your refund will be mailed to you by cheque or by EFT. No cash refunds will be given under any circumstances.":
            "只有金额超过 $25 时才能退款，且只能退还 M-Pass 账户中的全部剩余余额。申请退款时，将从你的余额中扣除 $25 的管理费。退款将以支票或电子转账（EFT）方式寄发给你。在任何情况下都不提供现金退款。",
        "The maximum balance your M-Pass account can be is $1,000. If you go over $1,000 your account may be frozen and we may refuse to allow further funds to be added to your M-Pass account. If your M-Pass account is frozen, contact Monash Connect.":
            "你的 M-Pass 账户余额上限为 $1,000。如果超过 $1,000，你的账户可能会被冻结，我们也可能拒绝你继续向 M-Pass 账户充值。如果你的 M-Pass 账户被冻结，请联系 Monash Connect。",
        "The maximum value of a single M-Pass account top up is $500.":
            "M-Pass 账户单次充值的最高金额为 $500。",
    },
    "mada-getting-started": {
        "Students studying Fine Art please be prepared to budget between $50 to $100 for your initial art supplies. You will be notified of material and levy requirements by staff on a project-by-project basis. Cost for each studio-based unit you enrol in will approximate $80 per semester. The Faculty of Art, Design and Architecture has an arrangement with a supplier to offer you these supplies at a discounted rate. Further information will be provided during Orientation week.":
            "修读美术（Fine Art）的学生请准备 $50 至 $100 的预算，用于购买初期的美术用品。教职员会按每个项目分别通知你所需的材料和费用。你注册的每门工作室类课程，每学期费用约为 $80。艺术、设计与建筑学院已与一家供应商达成安排，以折扣价向你提供这些用品。更多信息将在迎新周（Orientation week）期间提供。",
    },
    "majors-starting-with-g-geographical-science": {
        "Major required sequence | Recommended sequence | Recommended additional science units/core science unit | Science or non-science electives/core science unit\nSemester 1 | ATS1310 | Science sequence in Biological sciences or Chemistry | EAE1011 | CLI1100 or science elective\nSemester 2 | EAE1022 | Science sequence in Biological sciences ( BIO1042 recommended) or Chemistry | One level-one mathematics ":
            "主修必修顺序 | 推荐顺序 | 推荐的其他理科课程/核心理科课程 | 理科或非理科选修课/核心理科课程\n第 1 学期 | ATS1310 | 生物科学或化学的理科课程序列 | EAE1011 | CLI1100 或理科选修课\n第 2 学期 | EAE1022 | 生物科学（推荐 BIO1042）或化学的理科课程序列 | 一门一年级数学 ",
    },
    "majors-starting-with-p-physiology": {
        "Major required sequence | Or major required sequence | Core science units | Science or non-science elective\nSemester 1 | BIO1011 | CHM1011 or CHM1051 | One level-one mathematics or statistics unit from:\nMTH1020\nMTH1030 (or MTH1035 )\nSCI1020\nSCI1022\nSTA1010\nSCI1020 or STA1010 is recommended | Recommended - PHS1031\nSemester 2 | BIO1022 or BIO1042 | CHM1022 or CHM1052 | SCI1000 Science communication ":
            "主修必修顺序 | 或主修必修顺序 | 核心理科课程 | 理科或非理科选修课\n第 1 学期 | BIO1011 | CHM1011 或 CHM1051 | 从以下课程中选修一门一年级数学或统计课程：\nMTH1020\nMTH1030（或 MTH1035）\nSCI1020\nSCI1022\nSTA1010\n推荐选择 SCI1020 或 STA1010 | 推荐 - PHS1031\n第 2 学期 | BIO1022 或 BIO1042 | CHM1022 或 CHM1052 | SCI1000 科学传播 ",
    },
    "malaysia-academic-services-research-and-learning-onl": {
        "Monash Student Services Survey\n\n\nThe Monash Student Services Survey is now open. This survey helps Monash understand how student services, including SAS, are meeting your needs, as well as identify areas for improvement. The survey should take around 5 minutes to complete and you have the chance to win one of ten $250 prepaid e-gift cards.\nYour feedback help makes our services better!\n\n Learn more":
            "Monash 学生服务调查\n\n\nMonash 学生服务调查现已开放。这项调查帮助 Monash 了解包括 SAS 在内的学生服务是否满足你的需求，并找出需要改进的地方。完成调查大约需要 5 分钟，你还有机会赢取十张 $250 预付电子礼品卡中的一张。\n你的反馈能让我们的服务变得更好！\n\n 了解更多",
    },
    "malaysia-academic-services-student-academic-success": {
        "(We're unavailable outside working hours. Please allow up to 48 hours for a response.)":
            "（非工作时间我们无法回复。请预留最多 48 小时等待回复。）",
    },
    "malaysia-academic-staff2-dr--nadiahahmad": {
        "Ahmad, N. (2020) Gender Inequality, Mainstreaming Strategies and Perpetual Liminalities. In: Goh J.N., Bong S.A., Kananatu T. (eds) Gender and Sexuality Justice in Asia, Singapore: Springer. pp.3-16.\n\nAhmad, N. (2013) Examining the Exploitation of Indonesian Domestic Workers in Malaysia: Gender and National Policy Factors. In: Lee, Julian C.H. & Hopkins, J. (eds) Thinking Through Malaysia. Kuala Lumpur: Strategic Information Development Research (SIRD). pp.109-124.":
            "Ahmad, N.（2020）《性别不平等、主流化策略与永久的阈限状态》（Gender Inequality, Mainstreaming Strategies and Perpetual Liminalities）。载于：Goh J.N., Bong S.A., Kananatu T.（编）《亚洲的性别与性正义》（Gender and Sexuality Justice in Asia），新加坡：Springer。第 3-16 页。\n\nAhmad, N.（2013）《审视马来西亚印尼家庭佣工所受的剥削：性别与国家政策因素》（Examining the Exploitation of Indonesian Domestic Workers in Malaysia: Gender and National Policy Factors）。载于：Lee, Julian C.H. & Hopkins, J.（编）《思考马来西亚》（Thinking Through Malaysia），吉隆坡：Strategic Information Development Research（SIRD）。第 109-124 页。",
    },
    "malaysia-age-requirement": {
        "will be at least 16 years old at the time of enrolment and have not received a rank in another qualification Monash deems equivalent to an Australian Year 12 ATAR of at least 95 in the Victorian Certificate of Education BUT have the approval of the Head of School or Dean of the faculty, or":
            "在注册时年满 16 岁，且未在其他资格中获得 Monash 认定相当于维多利亚州教育证书（VCE）中澳大利亚 Year 12 ATAR 至少 95 分的排名，但已获得学院院长（Head of School）或学部院长（Dean of the faculty）的批准，或",
    },
    "malaysia-app-guide": {
        "My.App does not accept archive files, such as zip, rar, 7z, tar or iso. If you need to upload multiple files, we recommend combining them into a single word document or pdf file.":
            "My.App 不接受压缩文件，例如 zip、rar、7z、tar 或 iso。如果你需要上传多个文件，我们建议把它们合并成一个 Word 文档或 PDF 文件。",
    },
    "malaysia-apply-application-form": {
        "Take some time to read through all the instructions. Please complete all of the sections on the form. We can’t process incomplete applications until we receive the required documentation.":
            "请花些时间仔细阅读所有说明，并填写表格的所有部分。在收到所需文件之前，不完整的申请将不予受理。",
    },
    "malaysia-asean": {
        "Date\n\nSaturday, 10 October 2026\n\nPlatform\n\nZoom\n\nTime\n\n1pm - 2pm (Malaysian time)\n\nLoading...\n\nSomething went wrong, please try and reload the page.\n\nLoading...\n\nToo slow? Looks like it's taking a little more time than we'd thought.\n\nReload page\n\nContinue to wait...\n\nAgenda\n\nProgram schedule\n\nTime | Program\n1pm - 2pm | Ranked 31st globally:\nExplore Your Postgraduate Studies with Monash University ":
            "日期\n\n2026年10月10日，星期六\n\n平台\n\nZoom\n\n时间\n\n下午 1 点 - 下午 2 点（马来西亚时间）\n\n加载中...\n\n出现错误，请尝试重新加载页面。\n\n加载中...\n\n太慢了？看起来所需时间比我们预想的要长一些。\n\n重新加载页面\n\n继续等待...\n\n议程\n\n活动安排\n\n时间 | 活动\n下午 1 点 - 下午 2 点 | 全球排名第 31 位：\n与 Monash University 一起探索你的研究生学业 ",
    },
    "malaysia-chemical-engineering-what-our-graduates-say": {
        "A Chemical Engineering Degree truly holds the key to shape our future generations to come. Being in the O&G industry, we are constantly challenging ourselves to satisfy the global needs for energy in a sustainable manner and for me personally, being able to be a part of this solution is truly rewarding.\nNg Kee Seng\n2017 graduate\nAromatics Engineer\nExxonMobil KLTC\nAs Monash University’s motto said ":
            "化学工程学位确实是塑造我们未来几代人的关键。身处石油天然气（O&G）行业，我们不断挑战自我，以可持续的方式满足全球的能源需求；对我个人来说，能够成为这一解决方案的一部分，真的很有成就感。\nNg Kee Seng\n2017 届毕业生\n芳烃工程师（Aromatics Engineer）\nExxonMobil KLTC\n正如 Monash University 的校训所说 ",
    },
    "malaysia-courses-current-students2": {
        "Course and Unit Information\n\n• Handbook\n• Team Leaders\n• Faculty Policies & Guidelines\n• Pharmacy Honours Awards\n• Student Experiential Placements (StEPs)\n• Course Information Video: Bachelor of Pharmacy (Honours)\n• Course Information Video: Bachelor of Pharmaceutical Science\n\nEnrolment, Transfer and Exchange\n\n• Re-enrolment for Continuing Student\n• Campus Transfer\n• Semester in Australia (SIA)\n• ":
            "学位课程与课程信息\n\n• 手册（Handbook）\n• 团队负责人（Team Leaders）\n• 学院政策与指南\n• 药学荣誉学位奖项\n• 学生实践实习（Student Experiential Placements, StEPs）\n• 学位课程介绍视频：药学学士（荣誉）（Bachelor of Pharmacy (Honours)）\n• 学位课程介绍视频：药物科学学士（Bachelor of Pharmaceutical Science）\n\n注册、转换与交换\n\n• 在读学生重新注册\n• 转校区\n• 澳大利亚交流学期（Semester in Australia, SIA）\n• ",
    },
    "malaysia-courses-how-to-become-a-prp-candidate-at-mo": {
        "REQUIREMENTS\n\nCandidate must:\n\n• be a Malaysian\n• have completed BPharm degree in Malaysia that is approved by the Pharmacy Board of Malaysia.\n• currently enrolled as a graduate research student at Monash University Malaysia and must have successfully completed the confirmation of candidature (1st year milestone).\n• have an assigned research project related to pharmacy and pharmaceutical science.\n":
            "申请要求\n\n申请人必须：\n\n• 是马来西亚公民\n• 已在马来西亚完成经马来西亚药剂委员会（Pharmacy Board of Malaysia）认可的 BPharm 学位。\n• 目前以研究生研究型学生身份在莫纳什大学马来西亚分校就读，并且已顺利通过候选资格确认（confirmation of candidature，第一年里程碑）。\n• 已分配到与药学和药物科学相关的研究项目。\n",
    },
    "malaysia-engineering-bachelor-of-engineering-honours-4": {
        "Lysandra Koon Sue Ann\nBachelor of Robotics and Mechatronics Engineering (Honours)\nSystem-on-Chip (SoC) Design Engineer at Intel":
            "Lysandra Koon Sue Ann\n机器人与机电一体化工程学士（荣誉）\nIntel 片上系统（SoC）设计工程师",
    },
    "malaysia-examinations-results-exams-and-results": {
        "Don't use a hotspot internet connection - it may not provide adequate connectivity.":
            "不要使用手机热点上网——它的网络连接可能不够稳定。",
    },
    "malaysia-extra-curricular-activities-sass-films-film": {
        "Nasi Bungkus Cinema (or “Packed Lunch Cinema”) began as a series of lunch-time screenings showcasing the work of Arts and Social Sciences students. Since its inception, there have been regular screenings throughout the year, with student films taking on a range of topics including subject matter closely related to units taught within the school, such as environmental concerns, issues relating to race and ethnicity, gender stereotypes, and freedom of speech. Some of the films and students have gone on to achieve great success, such as Fikri Jermadi who won the Best Short Film award at the 2009 ":
            "Nasi Bungkus Cinema（意为“打包午餐影院”）最初是一系列午间放映活动，展示文学与社会科学学院学生的作品。自创办以来，全年都会定期举办放映，学生电影涉及各种主题，包括与学院所授课程密切相关的题材，例如环境问题、种族与族裔相关议题、性别刻板印象以及言论自由。其中一些影片和学生后来取得了巨大成功，例如 Fikri Jermadi，他在 2009 ",
    },
    "malaysia-facilities-career-development": {
        "With a Monash education, you join a global alumni community of more than 500,000 members. All Monash graduates have access to the University’s alumni programs, including network opportunities and many career-related events and programs.":
            "接受 Monash 教育，你将加入一个拥有超过 500,000 名成员的全球校友社群。所有 Monash 毕业生都可以参加大学的校友项目，包括人脉拓展机会以及众多与职业相关的活动和项目。",
    },
    "malaysia-frequent-asked-questions-faq-allocate-timet": {
        "I am not able to access the Moodle page for a unit. Whom do I contact for help?":
            "我打不开某门课程的 Moodle 页面。应该联系谁寻求帮助？",
    },
    "malaysia-frequent-asked-questions-faq-re-enrollment": {
        "I’ve an issue completing my re-enrolment due to the summer/winter,what can I do?":
            "由于夏季/冬季学期的原因，我在完成重新注册时遇到问题，该怎么办？",
    },
    "malaysia-frequent-asked-questions-faq-special-consid": {
        "I can’t complete my assignment and require an extension. How can I apply?":
            "我没法按时完成作业，需要申请延期。该如何申请？",
    },
    "malaysia-frequently-asked-questions-faq-enrollment": {
        "I have taken 96 credit points. Why can’t I enrol in Capstone unit in WES?":
            "我已经修了 96 学分。为什么无法在 WES 中注册综合实践课程（Capstone unit）？",
        "Why can’t I enrol in General Studies in WES?":
            "为什么无法在 WES 中注册通识课程（General Studies）？",
    },
    "malaysia-frequently-asked-questions-faq-enrolment-an": {
        "17. Why can’t I re-enrol via the Web Enrolment System (WES)?":
            "17. 为什么无法通过网上选课系统（WES）重新注册？",
    },
    "malaysia-frequently-asked-questions-faq-it-services": {
        "I couldn’t change my password.":
            "我改不了密码。",
        "I couldn’t change my password. Please refer to Password Information .":
            "我改不了密码。请参阅“密码信息”（Password Information）。",
    },
    "malaysia-frequently-asked-questions-faq-re-enrolment": {
        "I am not able to change my Major/Minor on WES?":
            "我在 WES 上没法更改主修/辅修？",
    },
    "malaysia-future-iufost-accreditation": {
        "IUFoST is the global federation of national scientific organisations representing more than 300,000 food scientists and technologists from over 75 countries. It has five regional groupings: ALACCTA representing Central and South America, EFFoST representing Europe, FIFSTA representing the ASEAN region, MENAFoST representing the Middle East and North Africa, and WAAFoST representing West Africa. IUFoST’s mission is to stimulate the ongoing exchange of knowledge in those scientific disciplines and technologies relating to the expansion, improvement, distribution, and conservation of the world's food supply.":
            "IUFoST（国际食品科学技术联盟）是由各国科学组织组成的全球性联合会，代表来自 75 个以上国家、超过 300,000 名食品科学家和技术人员。它下设五个区域组织：代表中美洲和南美洲的 ALACCTA、代表欧洲的 EFFoST、代表东盟地区的 FIFSTA、代表中东和北非的 MENAFoST，以及代表西非的 WAAFoST。IUFoST 的使命是促进与世界食品供应的扩大、改善、分配和保护相关的科学学科与技术之间持续的知识交流。",
    },
    "malaysia-gems-scholarship-thematic-cluster-predict-a": {
        "Impact: The collective projects aim to deliver a validated early-risk panel for severe dengue, ready-to-use SOPs and code for implementation, concise policy or clinical briefs for Malaysian decision-makers, and a prioritized, ADMET-screened shortlist of natural compounds for preclinical testing.":
            "影响：这些项目整体上旨在提供：一套经过验证的重症登革热早期风险检测组合、可直接使用的标准操作程序（SOP）及实施代码、面向马来西亚决策者的简明政策或临床简报，以及一份经 ADMET 筛选、按优先级排列、可用于临床前测试的天然化合物候选清单。",
    },
    "malaysia-honours-program-honours-feedback": {
        "The overall experience I had for my degree was both challenging and yet rewarding. My supervisor, Prof. Sadequr Rahman, had previously guided me for my third year research project and thus knew how to guide me in a way where I could work my hardest and achieve a good outcome. He was an extremely patient person who encouraged me to tackle my challenges head on in an independent manner but was also present to guide me if I couldn't solve a problem alone. He was tireless and adamant in his belief in me even when I was unsure of myself. I was able to tackle learning new software and refreshing my abilities with previous software I had learnt using the LINUX command based terminal due to him pushing me out of my comfort zone and his constant belief in me. Additionally, the various coursework assignments of the BSc(Hons) degree such as statistics and literature review, were extremely helpful for my research thesis writing while the journal article presentation helped a lot when it came to preparation of the research presentation. I had the appropriate facilities available for me to pursue my research with minimal disruptions which I am grateful for and life on campus was good as I had my course-mates, seniors and supervisor to continuously support me through the degree period.":
            "我在攻读学位期间的整体经历既充满挑战，又收获满满。我的导师 Sadequr Rahman 教授此前曾指导过我的三年级研究项目，因此他知道该如何引导我，让我尽最大努力并取得好的成果。他非常有耐心，鼓励我以独立的方式直面挑战，但在我独自解决不了问题时，他也总会在旁边指导我。即使在我对自己没有把握的时候，他也始终不知疲倦、坚定不移地相信我。正因为他把我推出舒适区并一直相信我，我才能够学习新的软件，并利用 LINUX 命令行终端重新熟练掌握以前学过的软件。此外，BSc(Hons) 学位的各项课程作业，例如统计学和文献综述，对我撰写研究论文非常有帮助，而期刊文章展示则在准备研究报告时帮了大忙。我有合适的设施来开展研究，几乎没有受到干扰，对此我十分感激；校园生活也很不错，因为在整个学位期间，我的同学、学长学姐和导师都一直支持着我。",
    },
    "malaysia-human-nutrition-talk": {
        "Date\n\nSaturday, 13 July 2024\n\nPlatform\n\nZoom\n\nTime\n\n3pm - 4.30pm\n\nLoading...\n\nSomething went wrong, please try and reload the page.\n\nLoading...\n\nToo slow? Looks like it's taking a little more time than we'd thought.\n\nReload page\n\nContinue to wait...\n\nAgenda\n\nProgram schedule\n\nTime | Program\n3pm - 3.15pm | Introduction to Monash University Malaysia\n3.15pm - 4pm | Fuelling Your Future: The Power of ":
            "日期\n\n2024年7月13日，星期六\n\n平台\n\nZoom\n\n时间\n\n下午 3 点 - 下午 4.30\n\n加载中...\n\n出现错误，请尝试重新加载页面。\n\n加载中...\n\n太慢了？看起来所需时间比我们预想的要长一些。\n\n重新加载页面\n\n继续等待...\n\n议程\n\n活动安排\n\n时间 | 活动\n下午 3 点 - 下午 3.15 | 莫纳什大学马来西亚分校介绍\n下午 3.15 - 下午 4 点 | 为你的未来加油：……的力量 ",
    },
    "malaysia-inbound-intern-abroad": {
        "We can match you with Malaysian corporations and non-governmental organisations (NGOs) to help you achieve your career goals.":
            "我们可以为你对接马来西亚的企业和非政府组织（NGO），帮助你实现职业目标。",
    },
    "malaysia-internship-amg5751-communication-industry-i": {
        "Due to the current situation, some host organisations will request students to attend onsite, some hosts will deliver the placement 100% remotely, and others will offer a hybrid placement, (a combination of remote and onsite).":
            "鉴于当前情况，部分接收单位会要求学生到现场实习，部分单位会以 100% 远程方式进行实习，还有一些则提供混合式实习（远程与现场相结合）。",
    },
    "malaysia-its-faq": {
        "I couldn’t change my password.":
            "我改不了密码。",
        "I couldn’t change my password. Please refer to Password Information .":
            "我改不了密码。请参阅“密码信息”（Password Information）。",
    },
    "malaysia-its-our-services-2": {
        "EndNote 20, 21, 25 Searches bibliographic databases on the Internet and organizes references, images, PDFs and other files. Windows macOS Install":
            "EndNote 20, 21, 25 检索互联网上的文献书目数据库，并整理参考文献、图片、PDF 及其他文件。Windows macOS 安装",
        "I couldn’t change my password.":
            "我改不了密码。",
        "I couldn’t change my password. Please refer to Password Information .":
            "我改不了密码。请参阅“密码信息”（Password Information）。",
        "RM1.10 per page / per side":
            "每页 / 每面 RM1.10",
    },
    "malaysia-jcsmhs-psychology": {
        "Course map from February 2024 intake onwards:":
            "2024年2月及之后入学适用的学位课程地图：",
    },
    "malaysia-mapel-lab-publications": {
        "Publications\n\n1. Affordances of an innovative ecosystem of multiple tabletops and Anatomy resources for supporting collaborative practical learning (2012). In J. Lee et al. (Eds.). Proceedings of the 20th International Conference on Computers in Education. Singapore: Asia-Pacific Society for Computers in Education. p. 79-82. ISBN 978-981-07-4651-3.\n2. Tapping Technology to give Formative Feedback ":
            "出版物\n\n1. 由多台桌面设备与解剖学资源组成的创新生态系统在支持协作式实践学习方面的功能可供性（2012）。载于 J. Lee 等（编），《第 20 届国际计算机教育大会论文集》。新加坡：亚太计算机教育学会。第 79-82 页。ISBN 978-981-07-4651-3。\n2. 借助技术提供形成性反馈 ",
    },
    "malaysia-master": {
        "You have outstanding opportunities to further your studies at Monash through postgraduate coursework or research degrees, including PhD programs. Our postgraduate degrees offer you personal enrichment and enhanced career opportunities.\n\nWe also provide scholarships to deserving honours, masters and PhD students. \n\nIf you’re interested in a research degree, consider possible research projects and topics that align with your interests, qualifications and experience. Look through Monash University’s research strengths by school for reference and identify potential supervisors. Further details on ":
            "你有很多机会在 Monash 继续深造，攻读授课型研究生学位或研究型学位，包括 PhD 项目。我们的研究生学位能丰富你的个人发展，并为你带来更好的职业机会。\n\n我们还为优秀的荣誉学位、硕士和 PhD 学生提供奖学金。 \n\n如果你有意攻读研究型学位，请考虑与你的兴趣、资历和经验相契合的研究项目和课题。你可以按学院查阅 Monash University 的优势研究领域作为参考，并物色潜在的导师。有关更多详情 ",
    },
    "malaysia-mechanical-engineering-why-choose-us": {
        "The Unique Value Proposition of this program is as follows:\n\n• Unique features: Tailored made Mechanical Design units, which coupled with External Design competitions, to enhance students’ learning experience.\n• Globally recognized degree: Accredited by Engineers Accreditation Council and Engineers Australia.\n• Career head-start: Cutting edge industry-driven and research-oriented projects to give ":
            "本项目的独特价值主张如下：\n\n• 独特亮点：量身定制的机械设计课程，并结合校外设计竞赛，提升学生的学习体验。\n• 全球认可的学位：获得工程师认证委员会（Engineers Accreditation Council）和澳大利亚工程师协会（Engineers Australia）认证。\n• 职业起步优势：前沿的产业驱动型和研究导向型项目，让你 ",
    },
    "malaysia-medicine-med5101": {
        "Education SIPs are aimed at developing and/or evaluating educational material for: patients, the general public, students or other health practitioners. That material could include: patient information sheet(s), website material, one or more YouTube clips, Podcast(s), infographics, an iSAP Case Study or new OSCE’s or PBLs etc. You would need to identify what is already available for the target audience and justify the need for your proposed new material. You will also need to story-book, develop and refine the material. If there is time, trial and evaluate the material and discuss the potential uses and outcomes of the new material.":
            "教育类 SIP 旨在为以下对象开发和/或评估教育材料：患者、公众、学生或其他医疗从业者。这些材料可以包括：患者资料单、网站内容、一个或多个 YouTube 短片、播客、信息图、iSAP 案例研究，或新的 OSCE 或 PBL 等。你需要了解目标受众目前已有哪些资料，并论证你所提出的新材料确有必要。你还需要为材料绘制故事板，并进行开发和完善。如果时间允许，还可以试用并评估这些材料，并讨论新材料的潜在用途和成效。",
    },
    "malaysia-orientation-faqs": {
        "What do I do if I can’t attend Orientation in person?":
            "如果我没办法亲自参加迎新活动（Orientation），该怎么办？",
    },
    "malaysia-orientation-for-new-students-e6001": {
        "Master of Advanced Engineering preview\n\nUnit Offering 2020\n\nUnit code | Unit title | Credit point | Semester 1 | Semester 2\nENG5001 | Advanced Engineering Data Analysis | 6cp | Yes\nCHE5885 | Principles and Practices for Sustainable Development | 6cp | Yes\nCIV5801 | Green Building | 6cp | Yes\nMEC5885 | Energy Efficiency and Sustainable Engineering | 6cp | Yes\nENG5002 | Engineering Entrepreneurship ":
            "高级工程硕士（Master of Advanced Engineering）预览\n\n2020 年课程开设情况\n\n课程代码 | 课程名称 | 学分 | 第 1 学期 | 第 2 学期\nENG5001 | 高级工程数据分析 | 6 学分 | 是\nCHE5885 | 可持续发展的原理与实践 | 6 学分 | 是\nCIV5801 | 绿色建筑 | 6 学分 | 是\nMEC5885 | 能源效率与可持续工程 | 6 学分 | 是\nENG5002 | 工程创业 ",
    },
    "malaysia-orientation-hub-enrolment-wes-and-timetable": {
        "[International Student] I do not have access to enrol in units.":
            "[国际学生] 我没有选课的权限。",
    },
    "malaysia-our-equipment-and-software-mass-spectromete": {
        "The Agilent 6550 iFunnel Quadrupole Time-of-Flight (Q-TOF) mass spectrometer delivers the lowest detection levels of any high-resolution LC/MS instrument. By incorporating Agilent Jet Stream technology and dual-stage ion funnel, the system can achieve a 10-fold increased sensitivity for selected molecules compared to an earlier generation Q-TOF. With the combination of ChipCube interface, the robust Agilent 6550 i-Funnel Q-TOF system can process protein/peptide samples derived from various backgrounds, including plant, snake venom and microorganisms, such as viruses, bacteria and fungi, blood ":
            "Agilent 6550 iFunnel 四极杆飞行时间（Q-TOF）质谱仪的检测限是所有高分辨率 LC/MS 仪器中最低的。该系统结合了 Agilent Jet Stream 技术和双级离子漏斗，对选定分子的灵敏度比上一代 Q-TOF 提高了 10 倍。配合 ChipCube 接口，性能稳健的 Agilent 6550 i-Funnel Q-TOF 系统可以处理来自多种来源的蛋白质/肽样品，包括植物、蛇毒以及病毒、细菌和真菌等微生物，以及血液 ",
    },
    "malaysia-our-services-printing-services": {
        "RM1.10 per page / per side":
            "每页 / 每面 RM1.10",
    },
    "malaysia-our-services-software-for-student-on-person": {
        "EndNote 20, 21, 25 Searches bibliographic databases on the Internet and organizes references, images, PDFs and other files. Windows macOS Install":
            "EndNote 20, 21, 25 检索互联网上的文献书目数据库，并整理参考文献、图片、PDF 及其他文件。Windows macOS 安装",
    },
    "malaysia-pdpa": {
        "Jabatan-jabatan atau agensi-agensi kerajaan yang berkaitan, pihak berkuasa berkanun":
            "相关的政府部门或机构、法定机构",
        "Sekiranya anda gagal untuk membekalkan maklumat wajib, kami mungkin tidak akan dapat memproses permintaan anda dan/atau membekalkan anda dengan perkhidmatan-perkhidmatan yang berkaitan.":
            "如果你未能提供必填信息，我们可能没办法受理你的请求和/或向你提供相关服务。",
        "dan pengawal selia industri; dan":
            "以及行业监管机构；以及",
    },
    "malaysia-pgfees": {
        "Master of Artificial Intelligence Coursework Full-time: 1.5-2 years (3-4 semesters)* Part-time: 3-4 years (6-8 semesters)* 64,080 (full course) 77,760 (full course)":
            "人工智能硕士 授课型 全日制：1.5-2 年（3-4 个学期）* 非全日制：3-4 年（6-8 个学期）* 64,080（整个学位课程） 77,760（整个学位课程）",
        "Master of Digital Business Coursework Full-time: 1.5 years (3 semesters) Part-time: 3 years (6 semesters) 66,960 (full course) 77,760 (full course)":
            "数字商务硕士 授课型 全日制：1.5 年（3 个学期） 非全日制：3 年（6 个学期） 66,960（整个学位课程） 77,760（整个学位课程）",
        "Postgraduate Certificate of Applied Engineering Coursework Full-time: 6 months (1 semester) Part-time: 1 year (2 semesters) 28,560 (full course) 32,640 (full course)":
            "应用工程研究生证书 授课型 全日制：6 个月（1 个学期） 非全日制：1 年（2 个学期） 28,560（整个学位课程） 32,640（整个学位课程）",
    },
    "malaysia-postgraduate-info-day-january-2026": {
        "Date\n\nSaturday, 17 January 2026\n\nVenue\n\nMonash University Malaysia\n\nTime\n\n11am - 2.30pm\n\nRegister your attendance now! ⬇️\n\nLoading...\n\nSomething went wrong, please try and reload the page.\n\nLoading...\n\nToo slow? Looks like it's taking a little more time than we'd thought.\n\nReload page\n\nContinue to wait...\n\nPROGRAM\n\nTime | Program\n11am - 11.30am | Registration\n11.30am - 12pm | Ranked #36 Globally:\n":
            "日期\n\n2026年1月17日（星期六）\n\n地点\n\n莫纳什大学马来西亚分校\n\n时间\n\n上午 11:00 - 下午 2:30\n\n立即登记参加！⬇️\n\n加载中……\n\n出错了，请尝试重新加载页面。\n\n加载中……\n\n太慢了？看来加载时间比我们预想的要长一些。\n\n重新加载页面\n\n继续等待……\n\n活动安排\n\n时间 | 活动\n上午 11:00 - 上午 11:30 | 签到登记\n上午 11:30 - 中午 12:00 | 全球排名第 36 位：\n",
    },
    "malaysia-postgraduate-info-session-mena": {
        "Date\n\nFriday, 23 October 2026\n\nPlatform\n\nZoom\n\nTime\n\n8pm - 9pm (GMT +3)\n\nLoading...\n\nSomething went wrong, please try and reload the page.\n\nLoading...\n\nToo slow? Looks like it's taking a little more time than we'd thought.\n\nReload page\n\nContinue to wait...\n\nAgenda\n\nProgram schedule\n\nTime | Program\n8pm - 9pm | Ranked 31st globally:\nExplore Your Postgraduate Studies with Monash University Malaysia\n\n":
            "日期\n\n2026年10月23日（星期五）\n\n平台\n\nZoom\n\n时间\n\n晚上 8:00 - 9:00（GMT +3）\n\n加载中……\n\n出错了，请尝试重新加载页面。\n\n加载中……\n\n太慢了？看来加载时间比我们预想的要长一些。\n\n重新加载页面\n\n继续等待……\n\n议程\n\n活动日程\n\n时间 | 活动\n晚上 8:00 - 9:00 | 全球排名第 31 位：\n与莫纳什大学马来西亚分校一起探索你的研究生学业\n\n",
    },
    "malaysia-postgraduate-overview": {
        "You have outstanding opportunities to further your studies at Monash through postgraduate coursework or research degrees, including PhD programs. Our postgraduate degrees offer you personal enrichment and enhanced career opportunities.\n\nWe also provide scholarships to deserving honours, masters and PhD students. \n\nIf you’re interested in a research degree, consider possible research projects and topics that align with your interests, qualifications and experience. Look through Monash University’s research strengths by school for reference and identify potential supervisors. Further details on ":
            "你有很多机会在 Monash 继续深造，攻读授课型研究生学位或研究型学位，包括 PhD 项目。我们的研究生学位能丰富你的个人发展，并为你带来更好的职业机会。\n\n我们还为优秀的荣誉学位、硕士和 PhD 学生提供奖学金。 \n\n如果你有意攻读研究型学位，请考虑与你的兴趣、资历和经验相契合的研究项目和课题。你可以按学院查阅 Monash University 的优势研究领域作为参考，并物色潜在的导师。有关更多详情 ",
    },
    "malaysia-psychology-courses-course-accreditation-bps": {
        "Course name: Bachelor of Psychological Science\n\nApproval Code: N/311/6/0068 (05/20) - MQA/SWA11799\n\nMalaysia\n\nAccreditation Body | Awarding Body | Date Granted | Date of Expiry | Registration No. / Accreditation Code\nMalaysian Qualifications Agency (MQA) | Government | 17 November 2018 | Not\napplicable | MQA/SWA11799\n\nAccreditation Body | Awarding Body | Date Granted | Recognized as equivalent to ":
            "学位课程名称：心理科学学士（Bachelor of Psychological Science）\n\n批准代码：N/311/6/0068 (05/20) - MQA/SWA11799\n\n马来西亚\n\n认证机构 | 颁授机构 | 授予日期 | 到期日期 | 注册编号 / 认证代码\n马来西亚资格认证机构（MQA） | 政府 | 2018年11月17日 | 不\n适用 | MQA/SWA11799\n\n认证机构 | 颁授机构 | 授予日期 | 认可等同于 ",
    },
    "malaysia-quitplastic-more-plastic-than-fish-by-2050": {
        "The damage caused by plastic debris in the ocean is estimated to be at least $13 billion per year. Marine lives are also affected as they can’t differentiate plastic from food. Just recently, a woman in Indonesia found a plastic spoon, a candy bar wrapper, plastic strap and a deodoriser cap inside the stomach of a fish she had purchased from the market. Fish are unable to break down plastic in their stomachs and often starve to death as a result of ingesting it.":
            "据估计，海洋塑料垃圾每年造成的损失至少达 $13 billion。海洋生物也深受其害，因为它们无法区分塑料和食物。就在最近，一名印度尼西亚女子在从市场买来的一条鱼的胃里，发现了一把塑料勺子、一张糖果包装纸、一根塑料捆扎带和一个除臭剂瓶盖。鱼类无法在胃中分解塑料，误食塑料后往往会因此饿死。",
    },
    "malaysia-rankings-bachelor-of-engineering-mechanical": {
        "Course Accreditation Pro‐Forma\n\nPreviously known as Bachelor of Engineering (Honours) in Mechanical Engineering\n\nMALAYSIA\n\nAccreditation Body | Awarding Body | Date Granted | Date of Expiry | Registration No/Accreditation Code\nMalaysian Qualifications Agency (MQA) | Government | 01 January 2022 | 31 December 2027 | MQA/FA7520\nEngineers Accreditation Council (EAC) | Professional Body | 2022 | 2027 ":
            "学位课程认证表（Pro‐Forma）\n\n原名 Bachelor of Engineering (Honours) in Mechanical Engineering（机械工程荣誉工学学士）\n\n马来西亚\n\n认证机构 | 颁授机构 | 授予日期 | 到期日期 | 注册编号/认证代码\n马来西亚资格认证机构（MQA） | 政府 | 2022年1月1日 | 2027年12月31日 | MQA/FA7520\n工程师认证委员会（EAC） | 专业机构 | 2022 | 2027 ",
    },
    "malaysia-re-enrolment-engineering-re-enrolment-guide": {
        "If you have passed all of the units to date or you are a July 2026 intake or October 2026 intake student, click on the respective engineering specialization below and refer to your commencing intake:":
            "如果你至今已通过所有课程，或者你是 2026年7月入学或 2026年10月入学的学生，请点击下方相应的工程专业方向，并查看你所属的入学批次：",
    },
    "malaysia-reputation": {
        "Sports Scholarship — RM5,000 fee waiver per semester for national athletes":
            "体育奖学金 — 国家级运动员每学期可获 RM5,000 学费减免",
    },
    "malaysia-safety-motor-vehicle-safety": {
        "• Consider the following tips when using your car and parking on Campus\n• Park in well lit areas where your car is visible.\n• Avoid parking next to trucks and vans.\n• Keep all items out of sight, especially valuables and loose change.\n• Remove GPS cradles and other signs of valuables in the car, make sure you wipe the suction marks off your windscreen.\n• Place GPS units and other valuables in the ":
            "• 在校园内用车和停车时，请留意以下建议\n• 将车停在光线充足、车辆清晰可见的地方。\n• 避免停在卡车和厢式货车旁边。\n• 不要把任何物品放在显眼处，尤其是贵重物品和零钱。\n• 取下 GPS 支架以及其他会暗示车内有贵重物品的物件，并擦掉挡风玻璃上的吸盘印。\n• 将 GPS 设备和其他贵重物品放在 ",
    },
    "malaysia-science-current": {
        "PhD\n\nAalina Sakiinah binti Mohd Fuad\nProject : Antimicrobial and Antibiofilm Activity of Snake Venom Peptide Against Bacteria\nCausing Chronic Wound\nMain Supervisor : Dr. Adzzie Shazleen binti Azman\nAkshaya Parasuraman\nProject : Transcriptomic and Proteomic Profiling of Malaysian Rice for Identification of Biomarkers Differentiating Weedy and Cultivated Rice\nMain Supervisor : A/Prof. Song Beng Kah\n":
            "PhD\n\nAalina Sakiinah binti Mohd Fuad\n项目：蛇毒肽对引起慢性伤口的\n细菌的抗菌及抗生物膜活性\n主导师：Adzzie Shazleen binti Azman 博士\nAkshaya Parasuraman\n项目：马来西亚稻米的转录组与蛋白质组分析，以鉴定区分杂草稻与栽培稻的生物标志物\n主导师：Song Beng Kah 副教授\n",
    },
    "malaysia-self-help-resources-scheduling-time": {
        "• Here are some practical things that you can do to help stop procrastinating and become more productive.\n\nBe honest\n\n• Admit to yourself and others that you've been putting off doing the task\n\nFind the right time to do it\n\n• When you finish a task that you enjoy, quickly switch over to work on the less attractive task that you have been avoiding\n• Work out what time or day you are most alert and ":
            "• 以下是一些实用的方法，可以帮助你停止拖延、提高效率。\n\n坦诚面对\n\n• 向自己和他人承认你一直在拖延这项任务\n\n找准合适的时间去做\n\n• 完成一项你喜欢的任务后，马上转去做你一直在逃避、不那么有吸引力的任务\n• 弄清楚你在一天中的什么时间、一周中的哪一天精力最充沛，并且 ",
    },
    "malaysia-study-0047": {
        "Uday P Kundap\nDoctor of Philosophy\nPostdoctoral Fellow at the University of Montreal Hospital Research Center":
            "Uday P Kundap\n哲学博士\n蒙特利尔大学医院研究中心博士后研究员",
    },
    "malaysia-study-0057": {
        "In the Doctor of Philosophy (PhD) program, you will conduct independent research on an extensive project in your chosen discipline, supported by a minimum of two academic supervisors throughout your doctoral candidature. Your study will result in a research thesis of 100,000 words, which makes a valuable contribution to the current body of knowledge on your chosen topic.":
            "在哲学博士（PhD）项目中，你将在所选学科领域独立开展一项大型研究项目，整个博士候选期间至少有两名学术导师为你提供指导。你的研究最终将形成一篇 100,000 字的研究论文，为你所选课题的现有知识体系作出有价值的贡献。",
    },
    "malaysia-study-abroad-global-study-tours": {
        "Deposit payment: $100. Payment details will be provided to successful applicants.":
            "押金：$100。付款详情将提供给成功入选的申请人。",
    },
    "malaysia-study-abroad-guide-ie-what-you-should-know": {
        "Exchange units may not always have a 100% equivalency match with your Monash University requirements.":
            "交换课程未必总能与你在 Monash University 的课程要求 100% 对等匹配。",
    },
    "malaysia-study-b2027": {
        "Koh Jiaway\nBachelor of Business and Bachelor of Communications\nAssociate Director at Business Angel Network of Southeast Asia (BANSEA)":
            "Koh Jiaway\n商学学士与传播学学士\n东南亚天使投资网络（BANSEA）副总监",
    },
    "malaysia-study-b6007": {
        "Our students have been to China, Japan, Hong Kong, India and Korea where they’ve visited companies such as Boeing, Crédit Agricole, Hewlett-Packard and Samsung.":
            "我们的学生曾前往中国、日本、香港、印度和韩国，参访过 Boeing（波音）、Crédit Agricole（东方汇理）、Hewlett-Packard（惠普）和 Samsung（三星）等企业。",
    },
    "malaysia-study-s3701": {
        "Anshika Sharma\nBachelor of Science (Biotechnology)\nBachelor of Science (Honours)\nDoctor of Philosophy\nScientist at Thermo Fisher Scientific":
            "Anshika Sharma\n理学学士（生物技术）\n理学荣誉学士\n哲学博士\nThermo Fisher Scientific 科学家",
    },
    "malaysia-support-and-scholarships-graduate-research": {
        "No | Position | Location | School | Application Status\n1 | Research Assistant | Malaysia | Jeffrey Cheah School of Medicine and Health Sciences | Open\nResearch Topic: AI and Medical Education, Assessment Research\n2 | Doctor of Philosophy (PhD) | Malaysia | School of Arts and Social Sciences | Open\nResearch Topic: Digital technology and health & wellbeing, Digital technology and the state, Digital ":
            "编号 | 职位 | 地点 | 学院 | 申请状态\n1 | 研究助理 | 马来西亚 | Jeffrey Cheah 医学与健康科学学院 | 开放申请\n研究课题：人工智能与医学教育、评估研究\n2 | 哲学博士（PhD） | 马来西亚 | 文学与社会科学学院 | 开放申请\n研究课题：数字技术与健康及福祉、数字技术与国家、数字 ",
    },
    "malaysia-tender-cafeteria": {
        "1 Monash University Malaysia reserves the right to request Operator’s sales turnover information for MUM planning purposes.":
            "1 莫纳什大学马来西亚分校保留要求经营者提供销售营业额信息的权利，以供 MUM 规划之用。",
        "1 Price range. The list will be submitted to the MUM’s Food Services and Operations Committee (FSOC) for endorsement.":
            "1 价格区间。该清单将提交 MUM 餐饮服务与运营委员会（FSOC）审批。",
        "1 The Operator must comply with the pork free Food & Beverage (F&B) policy adopted by MUM.":
            "1 经营者必须遵守 MUM 所实行的无猪肉餐饮（F&B）政策。",
        "1 The Proprietor or Company needs to have a valid Certificate of Registration with the Registrar of Business / Companies Commission of Malaysia.":
            "1 业主或公司须持有由马来西亚商业注册局 / 公司委员会（Registrar of Business / Companies Commission of Malaysia）签发的有效注册证书。",
        "1 The duration of the contract for operating the cafeteria is for a period of 2 years, with the option to extend for an additional of 2 (two) years, i.e. (2+2) and further extension if satisfactory.":
            "1 食堂经营合同期限为 2 年，可选择再续约 2（两）年，即（2+2），如表现令人满意，还可进一步续约。",
        "1 The proposed layout for the cafeteria is as attached.":
            "1 拟定的食堂平面布局见附件。",
        "1 The rental rate for the Cafeteria kiosk is based on size of the total space occupied:":
            "1 食堂档口的租金按所占用的总面积计算：",
        "1 Time of service is expected to be according to the proposed operating schedule.":
            "1 服务时间应按照拟定的营业时间表执行。",
        "2 All expenses related to the preparation and submission of the Proposal for the Cafeteria operations are to be borne solely by the Tenderer.":
            "2 与编制和提交食堂经营投标书相关的一切费用，均由投标人自行承担。",
        "2 Cafeteria Operator must submit a written application to Facilities Management to request for any increase beyond the approved food price range. All proposals for any price increase are subjected to approval by the FSOC. The Operator IS NOT ALLOWED to increase any food price range without the approval of the FSOC.":
            "2 食堂经营者如需将食品价格调高至核准价格区间以上，必须向设施管理部（Facilities Management）提交书面申请。所有涨价申请均须经 FSOC 批准。未经 FSOC 批准，经营者不得上调任何食品的价格区间。",
        "2 However, there will be other times when the cafeteria may need to be open, such as when there are special events and functions, which can take place beyond the scheduled operating hours, including weekends and public holidays.":
            "2 不过，食堂有时也可能需要在其他时间营业，例如举办特别活动和庆典时，这些活动可能在既定营业时间以外进行，包括周末和公共假期。",
        "2 Operator to provide feedback on the space allocated.":
            "2 经营者须就所分配的场地提供反馈意见。",
        "2 The Company profile is to be submitted.":
            "2 须提交公司简介。",
        "2 The Operator must demonstrate effort to promote sustainability through means of technology, source-verified and environmentally friendly purchasing (including minimal use of plastic packaging and utensils), and resource conservation.":
            "2 经营者必须展示其在推动可持续发展方面所作的努力，包括运用技术、采购来源可查证且环保的产品（包括尽量减少使用塑料包装和餐具），以及节约资源。",
        "2 The current indicative rental rate is RM8/sq.ft. (subject to change) and is inclusive of cafeteria compound cleaning and pests management.":
            "2 目前的参考租金为每平方英尺 RM8（可能调整），已包含食堂区域清洁和虫害防治费用。",
        "2 The successful Operator will be required to sign an Agreement with MUM.":
            "2 中标的经营者须与 MUM 签订协议。",
        "3 After the closing date of submission of tender, Monash University Malaysia will not entertain any further request or appeal.":
            "3 投标截止日期过后，莫纳什大学马来西亚分校将不再受理任何进一步的请求或申诉。",
        "3 Documentary evidence of Paid Up Capital such as Form 24, including Form 9, 49 and the latest Audited Financial Statements are to be furnished.":
            "3 须提供实缴资本的证明文件，例如 Form 24，以及 Form 9、Form 49 和最新的经审计财务报表。",
        "3 Fit-out standards guideline include the following:":
            "3 装修标准指引包括以下内容：",
        "3 Operator has the flexibility to introduce/replace food items to/on their menu within the approved price framework. For food items price that are not within the approved price range, clause 10.2 applies.":
            "3 经营者可在核准的价格框架内，灵活地在菜单中新增或更换菜品。如菜品价格不在核准的价格区间内，则适用第 10.2 条。",
        "3 The Operator must demonstrate an exceptional ability to adapt to emerging culinary trends, demographics, and socio-economic development.":
            "3 经营者必须展现出卓越的能力，以适应新兴的餐饮潮流、人口结构变化和社会经济发展。",
        "3 The Operator must open the kiosk throughout January to December. Any temporary closure of a place of business, other than on an official public holiday, requires prior approval from the Facilities Management. The Operator shall notify Facilities Management no later than 7 days before the intended date of closure, stating the reasons for the closure, and the proposed dates for the closure and reopening.":
            "3 经营者必须在 1 月至 12 月期间全年开放档口。除法定公共假期外，任何临时停业均须事先获得设施管理部（Facilities Management）批准。经营者须在拟停业日期前至少 7 天通知设施管理部，说明停业原因以及拟定的停业和恢复营业日期。",
        "3 The months of December and January will be rental free to compensate for the long semester break.":
            "3 12 月和 1 月免收租金，以弥补漫长学期假期带来的影响。",
        "4 All employees, especially food and beverage handlers, are required to comply with food safety requirements. It is mandatory for them to be given the TY2 / Typhoid Injection, Cholera and Hepatitis B injections, and their Health Certificates to be presented for verification.":
            "4 所有员工，尤其是餐饮从业人员，均须遵守食品安全要求。他们必须接种 TY2 / 伤寒疫苗、霍乱疫苗和乙型肝炎疫苗，并出示健康证明以供核查。",
        "4 Kitchen ventilation and exhaust system:":
            "4 厨房通风及排气系统：",
        "4 Monash University Malaysia is not obliged to return the tender documents or supporting documents the Tenderers submitted.":
            "4 莫纳什大学马来西亚分校没有义务退还投标人所提交的投标文件或证明文件。",
        "4 The Operator must be able to cater to the student and staff population during peak time (lunch time). The currently estimated population during peak time (11am - 2pm) is 4,000.":
            "4 经营者必须能够在高峰时段（午餐时间）满足学生和员工的用餐需求。目前估计高峰时段（上午 11 点至下午 2 点）的用餐人数为 4,000 人。",
        "4 The Operator must demonstrate the ability to provide world class service and serve campus community in an inclusive and respectful manner.":
            "4 经营者必须展现出提供世界一流服务的能力，并以包容和尊重的方式服务校园社区。",
        "4 The rental and utilities deposits will be collected in advance and is refundable after deduction of outstanding rental or utilities charges upon termination of rental agreement:":
            "4 租金押金和水电费押金将预先收取，租赁协议终止时，扣除未结清的租金或水电费后予以退还：",
        "5 Monash University Malaysia will send written notice to participants who have been shortlisted for tender interview.":
            "5 Monash University Malaysia 将以书面形式通知入围投标面试的参与者。",
        "5 The Operator must be able cater to diverse food requirements, such as Asian, Western, Healthy, Vegetarian, food prepared upon order and etc.":
            "5 经营方必须能够满足多样化的餐饮需求，例如亚洲菜、西餐、健康餐、素食、现点现做等。",
        "5 The Operator must be able to subscribe to the cashless payment options as prescribed by MUM (eg. Grab Pay).":
            "5 经营方必须能够开通 MUM 指定的无现金支付方式（例如 Grab Pay）。",
        "5 The Operator shall be able to produce a Food Safety Plan containing procedures on hygienic food storage, preparation, handling, waste management, hygiene, and pest control. These procedures are to be submitted for review by MUM.":
            "5 经营方须能够提交一份食品安全计划，内容包括食品卫生储存、制备、处理、废弃物管理、卫生及虫害防治等方面的程序。这些程序须提交 MUM 审核。",
        "5 Utilities consumption will be charged according to set tariff rates and a separate meter will be installed by MUM to capture utilisation data and bill on a monthly basis.":
            "5 水电费将按既定费率收取，MUM 将安装独立电表以记录用量数据，并按月计费。",
        "6 As part of the statutory requirements, the Operator is required to register their business under Food Safety Information System of Malaysia for Domestic (FOSIM) under the Ministry of Health.":
            "6 根据法定要求，经营方须在卫生部（Ministry of Health）下属的马来西亚国内食品安全信息系统（Food Safety Information System of Malaysia for Domestic，FOSIM）登记其业务。",
        "6 Gas consumption will be charged according to the reading on a meter installed by MUM and will be billed on a monthly basis.":
            "6 燃气费将根据 MUM 所安装燃气表的读数收取，并按月计费。",
        "6 Shortlisted tenderer(s) may be required to prepare their food products for food testing evaluation session.":
            "6 入围投标者可能需要为食品试吃评估环节准备其食品。",
        "6 The Operator shall also establish and implement a regular inspection program to ensure a high standard of food safety and hygiene.":
            "6 经营方还须建立并实施定期检查计划，以确保高标准的食品安全与卫生。",
        "7 Monash University Malaysia reserves the right to accept or reject any tender at their discretion without assigning any reason thereof.":
            "7 Monash University Malaysia 保留自行决定接受或拒绝任何投标的权利，且无需说明任何理由。",
        "7 The Operator must ensure that the kitchen and food operations will be led by an experienced kitchen manager with significant F&B exposure in medium to large scale food operations.":
            "7 经营方必须确保厨房及餐饮运营由一位经验丰富的厨房经理负责，该经理须在中大型餐饮运营方面拥有丰富的餐饮（F&B）从业经验。",
        "8 The decision by MUM of the successful Tender is final.":
            "8 MUM 对中标结果的决定为最终决定。",
        "9 Failure to comply with any of the above requirements during the tenancy period may result in remedial action including up to termination of the tenancy contract.":
            "9 租期内如未能遵守上述任何要求，可能会被采取整改措施，严重者可终止租赁合同。",
    },
    "malaysia-why-flexibility": {
        "Our Library and Learning Commons encourages learning through inquiry, collaboration, discussion and consultation. It integrates IT facilities and library services in a user-friendly environment. Students have access to over 340,000 ebooks, 100,000 e-journals and over 1000 electronic databases, online lectures, reading lists, and past exam papers. \n\nA canopy walkway provides a secure link to the Sunway Pyramid shopping centre via Sunway University, and you have many options to enjoy life on campus beyond the classroom.":
            "我们的图书馆与学习共享空间（Library and Learning Commons）鼓励通过探究、协作、讨论和咨询来学习。这里将 IT 设施与图书馆服务整合在一个便捷友好的环境中。学生可以使用超过 340,000 本电子书、100,000 种电子期刊和 1000 多个电子数据库，以及在线讲座、阅读书目和往年试卷。\n\n一条有顶棚的步道经由 Sunway University 安全连通 Sunway Pyramid 购物中心；课堂之外，你也有很多方式享受校园生活。",
    },
    "malaysia-workplace-wellbeing-centre-publications": {
        "Feng, X., Han, P., & Long, T. (2024). Teams’ stressors and flow experience: An energy-based perspective and the role of team mindfulness. Journal of Business Research, 183, 114860.":
            "Feng, X., Han, P., & Long, T. (2024). Teams’ stressors and flow experience: An energy-based perspective and the role of team mindfulness（团队压力源与心流体验：基于能量的视角及团队正念的作用）. Journal of Business Research, 183, 114860.",
    },
    "malaysia-young-scholars-program-ysp-what-our-young-s": {
        "Diana Agnes\nThe young scholar’s program has been a great beginner friendly way to delve into the world of research. At the start of the program, interns can choose from a range of different research paper questions which I found quite challenging since all the topics were interesting in their own ways. The project I chose was on covid-19 treatments which is fascinating and relevant. Throughout the program, we learnt many skills that better equipped us for writing a research paper. The workshops we had on different research software, writing techniques and how to write a research paper were very helpful. Following that, we also had multiple talks from experts on the field and even PHD students. To sum it all up, I found that the knowledge I gathered in this program was invaluable and I am looking forward to use it soon.":
            "Diana Agnes\n青年学者项目（young scholar’s program）是一个非常适合新手入门、深入了解科研世界的好机会。项目开始时，实习生可以从多个不同的研究论文题目中选择，我觉得这一步挺难的，因为每个题目都各有各的意思。我选的课题是关于 covid-19 的治疗方法，既有趣又贴近现实。在整个项目中，我们学到了很多技能，让我们更有能力去撰写研究论文。关于各种研究软件、写作技巧以及如何撰写研究论文的工作坊都非常有帮助。此外，我们还听了多场该领域专家甚至博士生的讲座。总而言之，我觉得在这个项目中积累的知识非常宝贵，也期待很快就能用上。",
    },
    "manage-your-science-studies-course-maps": {
        "2017 course maps\n\nCourse code | Course name and course requirements | Course map\nB2023 | Bachelor of Commerce and Bachelor of Science | Course map\nB2016 | Bachelor of Commerce Specialist and Bachelor of Science | Course map\nD3005 | Bachelor of Education (Honours) and Bachelor of Science | Course map\nE3007 | Bachelor of Engineering (Honours) and Bachelor of Science | Course map\nC2003 | Bachelor of ":
            "2017 年学位课程地图\n\n学位课程代码 | 学位课程名称及学位课程要求 | 学位课程地图\nB2023 | 商学学士和理学学士（Bachelor of Commerce and Bachelor of Science） | 学位课程地图\nB2016 | 商学专才学士和理学学士（Bachelor of Commerce Specialist and Bachelor of Science） | 学位课程地图\nD3005 | 教育学（荣誉）学士和理学学士（Bachelor of Education (Honours) and Bachelor of Science） | 学位课程地图\nE3007 | 工程学（荣誉）学士和理学学士（Bachelor of Engineering (Honours) and Bachelor of Science） | 学位课程地图\nC2003 | ……学士（Bachelor of） ",
    },
    "managing-money-cost-saving": {
        "Borrow DVDs from the on-campus libraries":
            "从校内图书馆借阅 DVD",
    },
    "managing-your-candidature-ethics": {
        "Please note: From January 2024, the completion of the online Human Research Ethics module available through myDevelopment is mandatory for all HDRs undertaking human research activities and who want to submit an ethics application for review to the Monash University Human Research Ethics Committee. The appreciation and compliance of ethical principles in research is also part of the academic research integrity module in professional development and can be found here.":
            "请注意：自 2024 年 1 月起，所有开展人类研究活动、并希望向 Monash University 人类研究伦理委员会提交伦理审查申请的 HDR 学生，都必须完成 myDevelopment 上的在线人类研究伦理模块。理解并遵守研究伦理原则也是专业发展中学术研究诚信模块的内容之一，可在此处找到。",
    },
    "managing-your-candidature-research-integrity-and-i": {
        "Please note: From January 2024, the completion of the online Human Research Ethics module available through myDevelopment is mandatory for all HDRs undertaking human research activities and who want to submit an ethics application for review to the Monash University Human Research Ethics Committee. The appreciation and compliance of ethical principles in research is also part of the academic research integrity module in professional development and can be found here.":
            "请注意：自 2024 年 1 月起，所有开展人类研究活动、并希望向 Monash University 人类研究伦理委员会提交伦理审查申请的 HDR 学生，都必须完成 myDevelopment 上的在线人类研究伦理模块。理解并遵守研究伦理原则也是专业发展中学术研究诚信模块的内容之一，可在此处找到。",
    },
    "medical-appointments": {
        "If you're a student (or family member) and you miss an appointment, or cancel less than 1 hour before your scheduled time, a $45 Fail to Attend fee will apply. Cancelling early means another student can get seen sooner – you can cancel anytime online or by phone.":
            "如果你是学生（或学生家属），错过预约或在预约时间前不到 1 小时取消，将被收取 $45 的爽约费（Fail to Attend fee）。尽早取消可以让其他学生更快就诊——你可以随时在线或通过电话取消。",
        "This policy applies to GP appointments for students and their families only. Fail To Attend fees for visitors remain unchanged at $60.":
            "此政策仅适用于学生及其家属的全科医生（GP）预约。访客的爽约费（Fail To Attend fee）保持不变，仍为 $60。",
    },
    "new-colombo-plan-mobility-program-assessment-crite": {
        "A limited number of grants up to $6,000 each are available to Monash University students for a selection of undergraduate Global Study Tours and Language Intensive Programs. These grants are awarded on the basis of the number of available grants.":
            "Monash University 学生可申请数量有限、每笔最高 $6,000 的资助，用于部分本科 Global Study Tours（海外游学）及 Language Intensive Programs（语言强化项目）。这些资助根据可提供的名额发放。",
    },
    "new-colombo-plan-semester-program-assessment-crite": {
        "A limited number of grants up to $15,000 each are available to Monash University students for study in a specific field of study in Indo-Pacific countries at selected exchange partners. If the number of available grants is less than the number of eligible students, students are selected on evaluation of their personal statement (if this was part of the program selection), on academic merit (the WAM in the student’s current degree at the time of being accepted into the program) and equity indicators..":
            "Monash University 学生可申请数量有限、每笔最高 $15,000 的资助，用于在印太地区国家的指定交换合作院校学习特定学科领域。如果可提供的资助名额少于符合条件的学生人数，将根据学生的个人陈述（如果项目选拔包含此项）、学业成绩（即学生被项目录取时当前学位的 WAM（加权平均分））以及公平指标进行选拔。",
    },
    "new-inplace": {
        "If a document you need to upload has multiple pages, scan all the pages into the one document. For example: If you have a two-sided form, you'll need to scan both sides into a single pdf and then upload it to InPlace.":
            "如果你需要上传的文件有多页，请将所有页面扫描到同一个文件中。例如：如果你有一份双面表格，你需要将两面都扫描成一个 pdf 文件，然后上传到 InPlace。",
    },
    "orion-heads": {
        "Andrew is a Lecturer in Ancient History in the Faculty of Arts, where he teaches a range of classes on the history, archaeology, and language of ancient Greece, Rome, and Egypt. His research focuses on what happened to the temples of Egypt after the death of Kleopatra, and how they interacted with the new Roman authorities. He has been part of the Non-Residential College community since 2016, when he started as deputy head of Orion, before taking over from the inestimable Louise Broadbent as Head in 2018. He grew up and did his schooling in the United States, with some time living in Scotland ":
            "Andrew 是文学院（Faculty of Arts）古代史讲师，教授古希腊、古罗马和古埃及的历史、考古及语言等一系列课程。他的研究聚焦于克娄巴特拉（Kleopatra）去世后埃及神庙的命运，以及这些神庙如何与新的罗马当局互动。他自 2016 年起加入非住宿书院（Non-Residential College）社区，最初担任 Orion 副院长，2018 年从令人敬重的 Louise Broadbent 手中接任院长。他在美国长大并完成学业，其间也曾在苏格兰生活过一段时间",
    },
    "other-costs-amenities": {
        "The amount you pay depends on your fee type and study load – and the maximum amount you can be charged depends on the year. For 2027, the maximum amount is $386.":
            "你需要支付的金额取决于你的学费类型和学习负荷——可收取的最高金额则因年份而异。2027 年的最高金额为 $386。",
    },
    "other-programs-university-of-warwick-programs": {
        "The Monash Warwick Alliance harnesses the collective strengths of two universities creating unique international opportunities for all. Spend a semester or year at the University of Warwick and immerse yourself in British culture. Generous travel grants of up to $2500 can get you on your way.":
            "Monash-Warwick 联盟（Monash Warwick Alliance）汇聚两所大学的共同优势，为所有人创造独特的国际机会。你可以在 University of Warwick 度过一个学期或一年，沉浸式体验英国文化。最高可达 $2500 的丰厚旅行补助助你启程。",
    },
    "other-programs-university-of-warwick-programs-2": {
        "The Monash Warwick Alliance harnesses the collective strengths of two universities creating unique international opportunities for all. Spend a semester or year at the University of Warwick and immerse yourself in British culture. Generous travel grants of up to $2500 can get you on your way.":
            "Monash-Warwick 联盟（Monash Warwick Alliance）汇聚两所大学的共同优势，为所有人创造独特的国际机会。你可以在 University of Warwick 度过一个学期或一年，沉浸式体验英国文化。最高可达 $2500 的丰厚旅行补助助你启程。",
    },
    "overseas-health-cover-2026-monash-oshc-price-list": {
        "Cover for one and two months is available only for extending existing policies.\n\nThese premiums are subject to change.\n\nRate prior to 1 July 2026 | Rate from 1 July 2026\n1 | $74 | $419 | $812 | $77 | $503 | $893\n2 | $145 | $835 | $1,616 | $151 | $1,002 | $1,778\n3 | $218 | $1,251 | $2,426 | $227 | $1,501 | $2,669\n4 | $292 | $1,668 | $3,235 | $304 | $2,002 | $3,559\n5 | $364 | $2,085 | $4,046 | $379 ":
            "一个月和两个月的保障仅适用于现有保单的延期。\n\n以上保费可能会有变动。\n\n2026年7月1日之前的费率 | 2026年7月1日起的费率\n1 | $74 | $419 | $812 | $77 | $503 | $893\n2 | $145 | $835 | $1,616 | $151 | $1,002 | $1,778\n3 | $218 | $1,251 | $2,426 | $227 | $1,501 | $2,669\n4 | $292 | $1,668 | $3,235 | $304 | $2,002 | $3,559\n5 | $364 | $2,085 | $4,046 | $379 ",
    },
    "phoenix-heads": {
        "Xavier has lived in Taiwan, the United States, Canada, and later on in Brisbane, Sydney, and Melbourne. He joined Monash in the middle of pandemic lockdown in 2020 and had quite a career change from nearly a decade of being a software engineer. He is the Chief Examiner of MADA Internships, and he also teaches into various Interaction Design/UX units in the Design Department. He enjoys musical theatre and performs in community venues and a good cup of hot chocolate":
            "Xavier 曾在台湾、美国、加拿大生活，后来又先后住在布里斯班、悉尼和墨尔本。他于 2020 年疫情封城期间加入 Monash，此前他当了将近十年的软件工程师，可谓是一次不小的职业转型。他是 MADA 实习项目（MADA Internships）的主考官（Chief Examiner），同时也在设计系（Design Department）讲授多门交互设计/UX 课程。他喜欢音乐剧，会在社区场馆登台演出，也喜欢来一杯好喝的热巧克力",
    },
    "planning-your-course-scholarships-and-prizes": {
        "This prize awards $3000 to the current student in a Bachelor of Fine Art specialisation who achieves the highest mark in the final studio project each year.":
            "该奖项每年向在最终工作室项目中取得最高分的美术学士（Bachelor of Fine Art）专业方向在读学生颁发 $3000 奖金。",
        "Valued at $25,000, the prize includes $10,000 for international travel, enabling the recipient to investigate a personally meaningful aspect of architectural practice in a global context. The remaining funds contribute directly to course costs, providing meaningful support throughout the Master’s program. The prize is awarded based on a holistic assessment of a student’s creativity, resilience, and openness to broader cultural and design discourse.":
            "该奖项价值 $25,000，其中 $10,000 用于国际旅行，让获奖者能够在全球背景下探究建筑实践中对其个人有意义的某一方面。其余资金直接用于学位课程费用，为整个硕士项目期间提供切实的支持。该奖项将根据对学生创造力、韧性以及对更广泛文化与设计讨论的开放态度的综合评估来颁发。",
    },
    "porto-itinerary": {
        "7 July | Pre-departure compulsory workshop\n6-hour in-person workshop at Monash Caulfield campus.\n13 – 19 July | Online pre-week\nStudents will be provided access to an online platform in advance to the program commencing to help connect them with fellow-participants.\n19 July | Students will be required to arrive in Porto by 19 July and check into accommodation, ready for the program to commence 20 ":
            "7月7日 | 出发前必修工作坊\n在 Monash Caulfield 校区举行的 6 小时线下工作坊。\n7月13日 – 19日 | 线上预备周\n项目开始前，学生将提前获得一个在线平台的访问权限，帮助他们与其他参与者建立联系。\n7月19日 | 学生须于7月19日前抵达波尔图（Porto）并办理住宿入住，为项目于 20 ",
    },
    "postgraduate-2026-postgraduate-electives-timetable": {
        "AI for lawyers: Practical applications and theory":
            "面向律师的 AI：实际应用与理论",
    },
    "postgraduate-2027-postgraduate-electives-timetable": {
        "AI for lawyers: Practical applications and theory":
            "面向律师的 AI：实际应用与理论",
    },
    "previous-tours-caulfield": {
        "Deposit payment: $100. Payment details will be provided to successful applicants.":
            "押金：$100。付款详情将提供给成功入选的申请人。",
    },
    "program-search-mig-in-prato-mon2750-monash-innovat": {
        "Students are responsible for obtaining visas for their studies undertaken overseas. Monash Abroad is not able to provide individual visa or immigration advice. If you require a specific visa to enter the destination country (e.g. you are an International student), you will need to contact the relevant Consulate General or Embassy in Melbourne or Kuala Lumpur for advice.":
            "学生须自行办理海外学习所需的签证。Monash Abroad 不能就个人签证或移民问题给出建议。如果你需要特定签证才能进入目的地国家（例如你是国际学生），你需要联系墨尔本或吉隆坡的相关总领事馆或大使馆寻求建议。",
    },
    "program-search-pharmacy-intensives-in-prato": {
        "Pay your $500 deposit to Reho Study Tours to secure your accommodation.":
            "向 Reho Study Tours 支付 $500 押金，以确保你的住宿。",
        "Students are responsible for obtaining visas for their studies undertaken overseas. Monash Abroad is not able to provide individual visa or immigration advice. If you require a specific visa to enter the destination country (e.g. you are an International student), you will need to contact the relevant Consulate General or Embassy in Melbourne or Kuala Lumpur for advice.":
            "学生须自行办理海外学习所需的签证。Monash Abroad 不能就个人签证或移民问题给出建议。如果你需要特定签证才能进入目的地国家（例如你是国际学生），你需要联系墨尔本或吉隆坡的相关总领事馆或大使馆寻求建议。",
        "Thirty Verrocchi Charity Fund Pharmacy Prato Scholarship of up to $6000 each;":
            "三十项 Verrocchi Charity Fund Pharmacy Prato 奖学金，每项最高 $6000；",
        "Three Pharmacy Travel Grant of up to $3000 each":
            "三项药学旅行补助（Pharmacy Travel Grant），每项最高 $3000",
    },
    "program-search-semester-in-prato": {
        "Additional travel grants of up to $10,000 may be available, depending on the number of units undertaken and the approved funding model. These grants are intended to supplement existing Monash Abroad support and assist with the overall costs associated with participating in the program.":
            "根据所修课程数量及获批的资助模式，你可能还可以获得最高 $10,000 的额外旅行补助。这些补助旨在补充 Monash Abroad 现有的支持，帮助你承担参与该项目的整体费用。",
        "Students are responsible for obtaining visas for their studies undertaken overseas. Monash Abroad is not able to provide individual visa or immigration advice. If you require a specific visa to enter the destination country (e.g. you are an International student), you will need to contact the relevant Consulate General in Melbourne for advice.":
            "学生须自行办理海外学习所需的签证。Monash Abroad 不能就个人签证或移民问题给出建议。如果你需要特定签证才能进入目的地国家（例如你是国际学生），你需要联系墨尔本的相关总领事馆寻求建议。",
    },
    "program-search-summer-in-prato": {
        "Students are responsible for obtaining visas for their studies undertaken overseas. Monash Abroad is not able to provide individual visa or immigration advice. If you require a specific visa to enter the destination country (e.g. you are an International student), you will need to contact the relevant Consulate General or Embassy in Melbourne or Kuala Lumpur for advice.":
            "学生须自行办理海外学习所需的签证。Monash Abroad 不能就个人签证或移民问题给出建议。如果你需要特定签证才能进入目的地国家（例如你是国际学生），你需要联系墨尔本或吉隆坡的相关总领事馆或大使馆寻求建议。",
    },
    "research-degrees-hdr-support-fund": {
        "The HDR (Higher Degree by Research) Support Fund is designed to assist eligible HDR students within the Faculty of Law by offering financial support for research-related expenses that are essential for the successful completion of their thesis. Funding of up to $2500 is available throughout the length of candidature. This funding can be used for various research-related activities and resources that contribute directly to the student's research project.":
            "HDR（Higher Degree by Research，研究型学位）支持基金旨在为法学院（Faculty of Law）符合条件的 HDR 学生提供资助，用于支付顺利完成论文所必需的研究相关开支。在整个学籍期间，最高可获得 $2500 的资助。这笔资金可用于各类直接服务于学生研究项目的研究相关活动和资源。",
    },
    "resources-assessment-feedback": {
        "NOTE: If you are requesting feedback for more than one unit, you will need to make multiple submissions of this form.":
            "注意：如果你要申请多门课程的反馈，需要分别多次提交此表格。",
    },
    "scholarships-sponsorships-and-awards-deans-equity": {
        "The awardee will receive a trophy and a prize of $500 or equivalent at an international campus.":
            "获奖者将获得一座奖杯及 $500 奖金（在国际校区则为等值奖金）。",
    },
    "science-science-honours": {
        "Monash offers over 360 types of scholarships, valued at up to $280,000. Some scholarships offer one-off payments while others continue for the length of your course. Learn more about Monash Scholarships.":
            "Monash 提供 360 多种奖学金，价值最高可达 $280,000。有些奖学金是一次性发放，有些则在你的整个学位课程期间持续发放。了解更多关于 Monash 奖学金的信息。",
    },
    "science-units-available-for-tabs-clayton-pg-summer-2": {
        "Unit code | Unit title | Credit points | Application, enrolment, teaching and important dates | Notes\nENS5930 | Sustainability internship\nTerm 1-57 | 12 | Standard teaching period dates | S6002 Master of Environment and Sustainability and S6006 Master of Green Chemistry and Sustainable Technologies students only.\nAn application is required to enrol in this unit.\nGNA5930 | Genomics internship | 12 ":
            "课程代码 | 课程名称 | 学分 | 申请、选课、教学及重要日期 | 备注\nENS5930 | 可持续发展实习（Sustainability internship）\nTerm 1-57 | 12 | 标准教学期日期 | 仅限 S6002 环境与可持续发展硕士（Master of Environment and Sustainability）和 S6006 绿色化学与可持续技术硕士（Master of Green Chemistry and Sustainable Technologies）学生。\n选修本课程需要提交申请。\nGNA5930 | 基因组学实习（Genomics internship） | 12 ",
    },
    "science-units-available-for-tabs-clayton-ug-summer": {
        "Unit code | Unit title | Credit points | Application, enrolment, teaching and important dates | Notes\nBCH3990 | Action in biochemistry research project | 6 | Non-standard dates | Applications close: 2 November 2026\nEAE3000 | Earth, atmosphere and environment research project | 6 | Non-standard dates | Applications close: 16 November 2026\nEAE3010 | Earth, atmosphere and environment: Special topics ":
            "课程代码 | 课程名称 | 学分 | 申请、选课、教学及重要日期 | 备注\nBCH3990 | 生物化学研究实践项目（Action in biochemistry research project） | 6 | 非标准日期 | 申请截止：2026年11月2日\nEAE3000 | 地球、大气与环境研究项目（Earth, atmosphere and environment research project） | 6 | 非标准日期 | 申请截止：2026年11月16日\nEAE3010 | 地球、大气与环境：专题（Earth, atmosphere and environment: Special topics） ",
    },
    "services-student-grants": {
        "If you're in financial hardship and need immediate support you may be eligible for the Emergency Grant payment of up to $500.":
            "如果你遇到经济困难并需要即时支持，你可能有资格获得最高 $500 的紧急补助（Emergency Grant）。",
    },
    "services-student-loans": {
        "you can borrow up to $3,000":
            "你最多可以借 $3,000",
        "you can borrow up to $750":
            "你最多可以借 $750",
    },
    "special-circumstances-documents": {
        "Photographs or medical images (for example, X-rays, CT scans or MRIs)":
            "照片或医学影像（例如 X 光片、CT 扫描或 MRI）",
    },
    "student-complaints": {
        "Outcomes vary, depending on the nature of your complaint and resolution you’re seeking. In some cases, your complaint may be upheld but we might not be able to offer exactly what you requested. If that happens, you’ll have the option to accept or decline the recommendation we provide.":
            "结果会因你投诉的性质以及你希望达成的解决方式而有所不同。在某些情况下，你的投诉可能会被认定成立，但我们未必能完全按照你的要求提供解决方案。如果出现这种情况，你可以选择接受或拒绝我们提出的建议。",
        "There are some outcomes we’re not able to provide through this process, including:":
            "有些结果我们无法通过这一流程提供，包括：",
    },
    "student-industry-engagement-final-year-project-opt": {
        "Gain Real-World Experience with an IIPGain hands-on experience and a competitive edge for your career. Apply your skills to real industry challenges, building your professional network, and enhancing your employability—all while earning an industry-funded scholarship.":
            "通过 IIP 获得真实工作经验通过实践积累经验，为你的职业发展赢得竞争优势。将你的技能应用于真实的行业挑战，拓展职业人脉，提升就业竞争力——同时还能获得由行业资助的奖学金。",
    },
    "study-opportunities-acicis-law-professional-practi": {
        "NCP Grants Up to $6,000 New Colombo Plan mobility grants are available to support eligible students. Are you eligible?":
            "NCP 补助 最高 $6,000 的新科伦坡计划（New Colombo Plan）流动补助可为符合条件的学生提供支持。你符合条件吗？",
        "Up to $6,000 New Colombo Plan mobility grants are available to support eligible students. Are you eligible?":
            "最高 $6,000 的新科伦坡计划（New Colombo Plan）流动补助可为符合条件的学生提供支持。你符合条件吗？",
    },
    "study-opportunities-indonesian-business--law-and-s": {
        "The IBLS also offers students the option to undertake a ‘professional placement’, enabling students to put their studies into practice and gain a real-world experience outside the classroom. Students are placed with local commercial firms, community-based organisations, government bodies, and non-governmental organisations (NGOs) and are given the opportunity to develop important skills in legal advocacy, public relations, administration, finance, research and reporting.":
            "IBLS 还为学生提供“专业实习”（professional placement）的选择，让学生将所学付诸实践，在课堂之外获得真实的工作经验。学生会被安排到当地商业公司、社区组织、政府机构和非政府组织（NGO），并有机会培养法律倡导、公共关系、行政管理、财务、研究和报告等方面的重要技能。",
    },
    "study-opportunities-monash-cambridge-pathway": {
        "The Cambridge pathway is currently supported by the Nick Auden International Study Scholarship. This Scholarship will support Monash Law students to undertake one of the three international pathway programs established by the Monash Law Faculty. Please note, availability of this scholarship is dependent on funding at the time and there may be multiple awardees for amounts up to $10,000.":
            "Cambridge 路径项目目前由 Nick Auden International Study Scholarship 资助。该奖学金将支持 Monash 法学院学生参加由 Monash 法学院设立的三个国际路径项目之一。请注意，该奖学金能否提供取决于当时的资金情况，并且可能会有多名获奖者，每人金额最高 $10,000。",
    },
    "study-opportunities-monash-king-college-pathway": {
        "The Kings College pathway is currently supported by the Nick Auden International Study Scholarship. This Scholarship will support Monash Law students to undertake one of the three international pathway programs established by the Monash Law Faculty. Please note, availability of this scholarship is dependent on funding at the time and there may be multiple awardees for amounts up to $10,000.":
            "Kings College 路径项目目前由 Nick Auden International Study Scholarship 资助。该奖学金将支持 Monash 法学院学生参加由 Monash 法学院设立的三个国际路径项目之一。请注意，该奖学金能否提供取决于当时的资金情况，并且可能会有多名获奖者，每人金额最高 $10,000。",
    },
    "study-tours-belgiumgermany": {
        "Selected students will enrol in unit ACX3500/5951 or BFX3871/5860 for the Summer Semester B (SSB-01) teaching period.":
            "入选学生将在夏季学期 B（SSB-01）教学期选修课程 ACX3500/5951 或 BFX3871/5860。",
    },
    "tips-asthma-and-allergies": {
        "Asthma is a condition where a person's airways become inflamed and narrow and produce extra mucus. This makes it difficult to breathe and can cause a feeling of tightness in the chest, a cough and wheezing. Asthma can be mild, but it can also interfere with daily activities; in some cases, it may lead to a medical emergency. Although there’s no cure, usually it can be controlled, and most people with asthma can stay active and have a healthy life.\n\nAsthma symptoms can be triggered by different things in different people. Common triggers include exercise, cigarette smoke, having a cold or flu, ":
            "哮喘是一种气道发炎、变窄并产生过多黏液的疾病。这会导致呼吸困难，并可能引起胸闷、咳嗽和喘息。哮喘可能很轻微，但也可能影响日常活动；在某些情况下，还可能引发医疗紧急情况。虽然哮喘无法根治，但通常可以得到控制，大多数哮喘患者都能保持活跃、过上健康的生活。\n\n不同的人，哮喘症状的诱因也各不相同。常见诱因包括运动、香烟烟雾、感冒或流感、",
    },
    "undergraduate-undergraduate-law-degree-changes": {
        "I’d prefer to complete the new structure of the degree, why can’t I change? \nThe updated degree structure is designed for students who are just beginning their studies. Because you’ve already commenced your course, you’re enrolled in the current version of the degree, and your completed units map to that structure. Continuing in the course you started is the best and most efficient pathway to finishing your degree on time.":
            "我更想按新的学位结构完成学业，为什么不能更换？\n更新后的学位结构是为刚开始学习的学生设计的。由于你已经开始修读你的学位课程，你注册的是该学位的现行版本，你已完成的课程也对应这一结构。继续修读你已开始的学位课程，是按时完成学位最好、最高效的途径。",
    },
    "unsatisfactory-progress": {
        "You may also provide supporting documentation. If your supporting documentation isn’t available by the due date, let the faculty know when you’ll be able to provide it before the specified deadline.":
            "你也可以提交证明材料。如果你的证明材料在截止日期前还没有准备好，请告知学院你能在规定期限之前的什么时候提交。",
    },
    "ursa-advisers": {
        "Hi, I am Aditi Mehta, I'm pursuing Master of Cyber Security. I like binge-watching TV shows and movies Shrinking being my fav at the moment), chilling at the beach reading a book, and going on small hikes. I am also passionate about food, I would not be able to pick just one meal to eat for the rest of my life. Looking forward to meeting you all and making new friends!!":
            "大家好，我是 Aditi Mehta，正在攻读网络安全硕士。我喜欢刷剧和看电影（目前最爱的是《Shrinking》），喜欢在海滩边放松看书，也喜欢短途徒步。我还热爱美食，要我余生只吃一道菜，我实在选不出来。期待与大家见面，结交新朋友！！",
    },
    "usa-loan-types": {
        "$31,000 (not more than $23,000 subsidised)":
            "$31,000（其中受资助部分不超过 $23,000）",
    },
    "yearly-payment-dates-2027-payment-dates": {
        "Teaching periods | Payment due dates\nSummer A – semester 1 (SS-S1-01)\nSummer semester B (SSB-01)\nTerm 1 (T1-57)\nTrimester 1 (T1-58)\nSemester 1 (extended) (S1-32) | 4 Jan\n4 Jan\n4 Jan\n4 Jan\n4 Jan\nSemester 2 (northern) (S2-60)\nSemester one (S1-01)\nFull-year (Extended) (FY-32)\nFull-year (FY-01)\nTerm 2 (T2-57) | 19 Feb\n19 Feb\n19 Feb\n19 Feb\n19 Feb\nTrimester 2 (T2-58)\nWinter semester (WS-01) | 14 May\n14 ":
            "教学期 | 付款截止日期\n夏季 A – 第一学期（SS-S1-01）\n夏季学期 B（SSB-01）\nTerm 1（T1-57）\nTrimester 1（T1-58）\n第一学期（延长）（S1-32） | 1月4日\n1月4日\n1月4日\n1月4日\n1月4日\n第二学期（北半球）（S2-60）\n第一学期（S1-01）\n全年（延长）（FY-32）\n全年（FY-01）\nTerm 2（T2-57） | 2月19日\n2月19日\n2月19日\n2月19日\n2月19日\nTrimester 2（T2-58）\n冬季学期（WS-01） | 5月14日\n14 ",
    },
}
