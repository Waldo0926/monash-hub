# Malaysia source reconciliation — 2026-11-08

Read-only review for #264. The existing fetcher identified itself, respected robots.txt and used its normal sequential pacing/retry cap. Only the already curated programme catalogue and five fee/intake sources were read. No production refresh, database write or service restart was performed. No HTML/page bodies are included in this document.

All 68 URLs returned valid HTML with HTTP 200: 63 programme destinations (61 catalogue destinations plus two existing curated destinations), two fee indexes and three intake pages. Of the programme titles, 62/63 match the reviewed qualification identities. Fourteen expose one unambiguous Handbook course code through the extracted links; other codes remain unknown, not guessed.

Both fee indexes explicitly identify **2027**. October explicitly names its **October 2027** available-course list; the exact 21-name reviewed list and all three general deadline pairs were rechecked. A listed degree and a future deadline do not prove open applications. The Counselling page has an undated current closed notice; it does not certify closure for every future intake.

**Identity review required:** the Science fee row says `Master of Science`, while its linked programme title is `Master of Science (Research)`. These must remain unverified as an exact qualification match; no global title-normalization exception is added. The existing Business/Computer Science versus Business/Digital Media fee-link conflict remains separately flagged.

## Fee/index evidence

| URL | Fetched title | Content hash | Checked (UTC) |
| --- | --- | --- | --- |
| https://www.monash.edu.my/study/undergraduate/fees | Fees | `7744bdc1f2672ed306cfcf2fe62685d5889ae60da296e4dd121877c670990bc0` | 2026-11-08T09:39:44.607253+00:00 |
| https://www.monash.edu.my/study/postgraduate-and-research/fees | Fees | `1e9171993d43acfd987be2300bf165fbe6a46ed32903e3f3563ed425ca5cbd30` | 2026-11-08T09:39:48.681827+00:00 |
| https://www.monash.edu.my/study/apply/intake-periods/october-intake | October intake | `6ee8eddb33ccb4ef21c1c7789e893c93a068d4e5c7759af3c1a0e298cb00ed72` | 2026-11-08T09:39:53.258791+00:00 |
| https://www.monash.edu.my/study/apply/intake-periods/february-intake | February intake | `310eb69aebbc4ba59d7fef0b9c27a335677c5cdf39bd1f33a5b588e279e458ce` | 2026-11-08T09:39:55.277377+00:00 |
| https://www.monash.edu.my/study/apply/intake-periods | Intake periods | `20f2f168717f3c7ee8ef51f6f2a7862794fe0bea41653d4ffa76d0d1572eb069` | 2026-11-08T09:40:01.543538+00:00 |

## Programme reconciliation

“Matched” proves source identity, not application availability. Titles remain in the original language. “Unknown” codes are not evidence of discontinuation.

| Source | Fetched qualification title | Identity | Handbook code | Current notice | Content hash |
| --- | --- | --- | --- | --- | --- |
| https://www.monash.edu.my/study/postgraduate-and-research/arts-social-sciences/master-communications-media-studies | Master of Communications and Media Studies | Matched | Unknown | not_verified | `c4c5a498e7c00bf19820f65737f71c890d04284e11bba7864de69039814aeb23` |
| https://www.monash.edu.my/study/postgraduate-and-research/arts-social-sciences/phd | Doctor of Philosophy (PhD) | Matched | Unknown | not_verified | `ae23d01d0d632de375e8b22e996d71f141b7999d8043a49d3b00d5bd6e40e1ec` |
| https://www.monash.edu.my/study/postgraduate-and-research/business/diploma-business-commerce | Postgraduate Diploma in Business and Commerce | Matched | Unknown | not_verified | `cd5b6fc326f5707e6edbba6e3a5d6e7bf5a8530ebd722c19ea0961cff16c88e0` |
| https://www.monash.edu.my/study/postgraduate-and-research/business/master-international-business | Master of International Business | Matched | Unknown | not_verified | `1cc4f244c675bb34005a99e46a07091e513be7bd3901c514229ad797f8e5e18c` |
| https://www.monash.edu.my/study/postgraduate-and-research/business/master-of-digital-business | Master of Digital Business | Matched | B6033 | not_verified | `5ed1b1f76d7b7f0208eebd473fc21518c036ad6e4b83e25c65493aee6b77e590` |
| https://www.monash.edu.my/study/postgraduate-and-research/business/master-philosophy | Master of Philosophy | Matched | Unknown | not_verified | `49644cc29fcddfe220adcab57e0cdf0fbfb9dc877c5042eabd9e5602c0802b31` |
| https://www.monash.edu.my/study/postgraduate-and-research/business/phd | Doctor of Philosophy (PhD) | Matched | Unknown | not_verified | `bb9234be998d099c11c30d0fbf20e766e2306e0f2e2293966d1c301de5cd4cde` |
| https://www.monash.edu.my/study/postgraduate-and-research/engineering/master-engineering-science-research | Master of Engineering Science (Research) | Matched | Unknown | not_verified | `7c37e83a6a85520e5b6473ee13d13e4306a2ef656e49f9f8a0e0596483608b2a` |
| https://www.monash.edu.my/study/postgraduate-and-research/engineering/master-of-applied-engineering | Master of Applied Engineering | Matched | E6013 | not_verified | `4a4c8cc3d5ed22e660bad69b8f1442c94b70132f82cc03ae48c4b17e500d5fd8` |
| https://www.monash.edu.my/study/postgraduate-and-research/engineering/phd | Doctor of Philosophy (PhD) | Matched | Unknown | not_verified | `e42380df61fbe942bf01c17d2a9631aec69407a349c09d97b44bcb1f6a1ff8d4` |
| https://www.monash.edu.my/study/postgraduate-and-research/engineering/postgraduate-certificate-of-applied-engineering | Postgraduate Certificate of Applied Engineering | Matched | Unknown | not_verified | `1f74faed267feecfe70c6eee8696589c4e1de5b1ff5b0363c37b2d3f9958662d` |
| https://www.monash.edu.my/study/postgraduate-and-research/information-technology/master-business-information-systems | Master of Business Information Systems | Matched | C6003 | not_verified | `899bb6d97dbcc4dd027c5952c514ab3175453da93cd2aa1eb3049bd9c744aa9c` |
| https://www.monash.edu.my/study/postgraduate-and-research/information-technology/master-of-artificial-intelligence | Master of Artificial Intelligence | Matched | C6007 | not_verified | `6178a3720717bff761f15d431a8dcf6aac92a218d6da7c8ac3a9526354705d4d` |
| https://www.monash.edu.my/study/postgraduate-and-research/information-technology/master-of-data-science | Master of Data Science | Matched | C6004 | not_verified | `40cc9552c4bdd6f8eab775db2b5ad95e9f2f96c4bbf56a6a6896e17da4d8e0e5` |
| https://www.monash.edu.my/study/postgraduate-and-research/information-technology/master-philosophy | Master of Philosophy | Matched | Unknown | not_verified | `53c26c38f28e5485599fbbcb61d487a7f83e74ac54864692c0d500f51727c4e7` |
| https://www.monash.edu.my/study/postgraduate-and-research/information-technology/phd | Doctor of Philosophy (PhD) | Matched | Unknown | not_verified | `573b2c9b17e148721d1d1d8ca2a8e86938e6eedfa441344c3eefadfbc45f3595` |
| https://www.monash.edu.my/study/postgraduate-and-research/medicine-health-sciences/master-biomedical-science | Master of Biomedical Science | Matched | Unknown | not_verified | `48550c231707b8c967ed3d0baf55c0f58673cfe4e1720d89f5282cc4d8e4c107` |
| https://www.monash.edu.my/study/postgraduate-and-research/medicine-health-sciences/master-of-biotechnology | Master of Biotechnology | Matched | M6030 | not_verified | `df423bc1e127ded6e609c84402f51c07ac601f19e3534869d8b1e5fdae72ed9c` |
| https://www.monash.edu.my/study/postgraduate-and-research/medicine-health-sciences/master-of-clinical-psychology | Master of Clinical Psychology | Matched | Unknown | not_verified | `a3442f00453a2c568bde490583fe91db9bd124aa36667613a1c79f1dd9d29672` |
| https://www.monash.edu.my/study/postgraduate-and-research/medicine-health-sciences/master-of-professional-counselling | Master of Professional Counselling | Matched | D6006 | closed | `c96821ecb101f2db1c15bf414fd4b047056686e5b04ef070d85aceb6b80ce6ed` |
| https://www.monash.edu.my/study/postgraduate-and-research/medicine-health-sciences/phd | Doctor of Philosophy (PhD) | Matched | Unknown | not_verified | `84cf00dd38a168d12fee628c331065cf967160e0c69b0528e0f4c0c859eb388b` |
| https://www.monash.edu.my/study/postgraduate-and-research/pharmacy/doctor-of-philosophy-phd | Doctor of Philosophy (PhD) | Matched | Unknown | not_verified | `79c5a78227e2063ad1146c951798d95b2c647692e14d74259d926bcdfb8000c4` |
| https://www.monash.edu.my/study/postgraduate-and-research/pharmacy/master-of-pharmaceutical-science | Master of Pharmaceutical Science | Matched | P6005 | not_verified | `01c727b7fb7d62c5a0cf2554576de32fd41e195d674176f8658b00508e25ca06` |
| https://www.monash.edu.my/study/postgraduate-and-research/pharmacy/master-of-philosophy | Master of Philosophy | Matched | Unknown | not_verified | `f7fb97775583e36ff325f7be2f362261d625b78aeee6cf274a2053b39d82ef17` |
| https://www.monash.edu.my/study/postgraduate-and-research/science/master-science | Master of Science (Research) | Review required | Unknown | not_verified | `119af4d6b8a08a4ac14ac64e08646a3e10ee914b000fa136f813fcbf6bbd14f0` |
| https://www.monash.edu.my/study/postgraduate-and-research/science/phd | Doctor of Philosophy (PhD) | Matched | Unknown | not_verified | `f200c541aeaacbc0abba4834915ee50db53a015b8d7f235d78348cd0ff5b08bd` |
| https://www.monash.edu.my/study/undergraduate/arts-social-sciences/bachelor-arts-honours | Bachelor of Arts (Honours) | Matched | A3701 | not_verified | `b8a49287d306e5a0abf65271be79a21be0ab7c24245ba5c6c37152f91b717f53` |
| https://www.monash.edu.my/study/undergraduate/arts-social-sciences/bachelor-arts-social-sciences | Bachelor of Arts and Social Sciences | Matched | Unknown | not_verified | `82d2c9634face062c40ea30d2478fd6b408be27001ff6e975794de5babf02ad5` |
| https://www.monash.edu.my/study/undergraduate/arts-social-sciences/bachelor-of-digital-media-and-communication | Bachelor of Digital Media and Communication | Matched | Unknown | not_verified | `d9db87ef6388a95c7d860d1eda531be0db190d07d80de29a53d8067f47c62a9f` |
| https://www.monash.edu.my/study/undergraduate/business/bachelor-business-commerce | Bachelor of Business and Commerce | Matched | Unknown | not_verified | `9226ed0baa917d5f39b379161937d3e1aff136b9f266f35c6ab6cc6a35d8de89` |
| https://www.monash.edu.my/study/undergraduate/business/bachelor-business-commerce-bachelor-communication | Bachelor of Business and Commerce and Bachelor of Digital Media and Communication | Matched | Unknown | not_verified | `08451d70561268cd75dfe685bdae67a2af5369a179886c88f4a6a21b6edd63ef` |
| https://www.monash.edu.my/study/undergraduate/business/bachelor-business-commerce-bachelor-computer-science | Bachelor of Business and Commerce and Bachelor of Computer Science | Matched | B2048 | not_verified | `fb2642249e0606f0e1c52440d0c4156c6dbe960d73941d6c4b0aa3849d4b9ad0` |
| https://www.monash.edu.my/study/undergraduate/business/bachelor-business-commerce-honours | Bachelor of Business and Commerce (Honours) | Matched | Unknown | not_verified | `bdda51039c72bdcfbd5d74e8ab6e42b6dbb04664959378c7d678763071854665` |
| https://www.monash.edu.my/study/undergraduate/business/bachelor-in-actuarial-analytics | Bachelor in Actuarial Analytics | Matched | Unknown | not_verified | `8288e28a753a5e12f8e44102b522d43e961c1d3a887ca73f3e78f8e9b64b410d` |
| https://www.monash.edu.my/study/undergraduate/business/bachelor-of-digital-business | Bachelor of Digital Business | Matched | B2049 | not_verified | `0a35fc6d2565d622130819bd769cb01795dcb33d4663f6d8f42c47b39a139dcf` |
| https://www.monash.edu.my/study/undergraduate/engineering/bachelor-of-biomedical-engineering-honours | Bachelor of Biomedical Engineering (Honours) | Matched | Unknown | not_verified | `914de7c51be47ed988af416217546ba9bc37e34aaed08bf4fa7aa1d632143696` |
| https://www.monash.edu.my/study/undergraduate/engineering/bachelor-of-engineering-honours-in-chemical-engineering | Bachelor of Chemical Engineering (Honours) | Matched | Unknown | not_verified | `df630d8e2a533c89dcc9bc2c910c298c9aa11d1cb488723e7109a495696eb932` |
| https://www.monash.edu.my/study/undergraduate/engineering/bachelor-of-engineering-honours-in-civil-engineering | Bachelor of Civil Engineering (Honours) | Matched | Unknown | not_verified | `385e62833c8623c3d4efc7b52bb0565422f8e607b2efaceddad553077a0a00cb` |
| https://www.monash.edu.my/study/undergraduate/engineering/bachelor-of-engineering-honours-in-electrical-and-computer-systems-engineering | Bachelor of Electrical and Computer Systems Engineering (Honours) | Matched | Unknown | not_verified | `5cd7d134ac50ac6e15db60e1897db74354e2eab3a4b6daa36fb69703df71f023` |
| https://www.monash.edu.my/study/undergraduate/engineering/bachelor-of-engineering-honours-in-mechanical-engineering | Bachelor of Mechanical Engineering (Honours) | Matched | Unknown | not_verified | `d68ce35267f479686b24cbbc31c86cf49558554e329a019b7482adbb141e20c6` |
| https://www.monash.edu.my/study/undergraduate/engineering/bachelor-of-engineering-honours-in-mechatronics-engineering | Bachelor of Robotics and Mechatronics Engineering (Honours) | Matched | Unknown | not_verified | `d0cc35b711566d986a268e294a2606e503fd915ee245c21bb196387f2590933c` |
| https://www.monash.edu.my/study/undergraduate/engineering/bachelor-of-materials-engineering-honours | Bachelor of Materials Engineering (Honours) | Matched | Unknown | not_verified | `08b2de136743a48069722c3c1d8a0e08288a66631a4b9abe405ff8eb5eada6e9` |
| https://www.monash.edu.my/study/undergraduate/engineering/bachelor-of-software-engineering-honours | Bachelor of Software Engineering (Honours) | Matched | Unknown | not_verified | `e15364c0302f590ebdd8b1b5529c2ef66339721c662f01b6670fc8ea9542a041` |
| https://www.monash.edu.my/study/undergraduate/information-technology/bachelor-computer-science | Bachelor of Computer Science | Matched | Unknown | not_verified | `950f4f29e9fc84fd38067152c8f7e960f8c583576626d04bf7d9b27cad998a1b` |
| https://www.monash.edu.my/study/undergraduate/information-technology/bachelor-of-computer-science-honours | Bachelor of Computer Science (Honours) | Matched | Unknown | not_verified | `ccc89c5dc252916f9f2febf81170213c4448cade0d6afa8b0730e70c72ddc967` |
| https://www.monash.edu.my/study/undergraduate/information-technology/bachelor-of-computer-science-in-artificial-intelligence | Bachelor of Computer Science in Artificial Intelligence | Matched | Unknown | not_verified | `c3d430c31bdd9194fdc873642ee6df6479aa0ee698e5b89695bc63014f8be73f` |
| https://www.monash.edu.my/study/undergraduate/information-technology/bachelor-of-computer-science-in-data-science | Bachelor of Computer Science in Data Science | Matched | Unknown | not_verified | `87c7dd09ab280856f992ae8754283e0f47952a80fcca201bca7df5ea7e9e6236` |
| https://www.monash.edu.my/study/undergraduate/jeffrey-cheah-school-medicine-health-sciences/bachelor-medical-science-doctor-medicine | Bachelor of Medical Science and Doctor of Medicine | Matched | Unknown | not_verified | `bdab0ecc4c8d7b67b0a3a7536fcc00f1ae3230406b6d2c0f747111b23084b3c1` |
| https://www.monash.edu.my/study/undergraduate/jeffrey-cheah-school-medicine-health-sciences/bachelor-medical-science-honours | Bachelor of Medical Science (Honours) | Matched | M3701 | not_verified | `8ee65d93a2de641d85713d9fdfaba0aa8cab0cf17a33109319bb58b9990c532c` |
| https://www.monash.edu.my/study/undergraduate/jeffrey-cheah-school-medicine-health-sciences/bachelor-of-health-sciences-honours | Bachelor of Health Sciences (Honours) | Matched | Unknown | not_verified | `b37539256e02a544369d18998714ef6b2bec64557021e88e126fccc8c889d9e9` |
| https://www.monash.edu.my/study/undergraduate/jeffrey-cheah-school-medicine-health-sciences/bachelor-of-human-nutrition | Bachelor of Human Nutrition | Matched | Unknown | not_verified | `880ddd3a668ac3f15aa19d4a37df4539a62f1c9c08b4145bee12febef8c82834` |
| https://www.monash.edu.my/study/undergraduate/jeffrey-cheah-school-medicine-health-sciences/bachelor-of-psychology | Bachelor of Psychology | Matched | Unknown | not_verified | `d8b91f3edc6f566c1175ab571a01d532d2926bfe2cea9f1769a11f1f02122975` |
| https://www.monash.edu.my/study/undergraduate/jeffrey-cheah-school-medicine-health-sciences/bachelor-psychological-science-business | Bachelor of Psychology and Business | Matched | Unknown | not_verified | `0dbe81869f873a4af7200aac7b4544105ddbad9be49ec8ba9a3136abd97058ba` |
| https://www.monash.edu.my/study/undergraduate/jeffrey-cheah-school-medicine-health-sciences/bachelor-psychology-and-business | Bachelor of Psychology and Business | Matched | Unknown | not_verified | `0dbe81869f873a4af7200aac7b4544105ddbad9be49ec8ba9a3136abd97058ba` |
| https://www.monash.edu.my/study/undergraduate/jeffrey-cheah-school-medicine-health-sciences/bachelor-psychology-honours | Bachelor of Psychology (Honours) | Matched | Unknown | not_verified | `06f70deee665146857f864e3604758b50dc1d3a93ad2e0eea5718f7076dc3891` |
| https://www.monash.edu.my/study/undergraduate/pharmacy/bachelor-of-pharmaceutical-science | Bachelor of Pharmaceutical Science | Matched | Unknown | not_verified | `4f024edd8a23bc5675a467865c90161ac14a75fc57067de06a6311ff49f2bc2b` |
| https://www.monash.edu.my/study/undergraduate/pharmacy/bachelor-of-pharmaceutical-science-honours | Bachelor of Pharmaceutical Science (Honours) | Matched | P3701 | not_verified | `b53c29984b14df8b7f1b1f1d023f0de1bdfe95d24191bc16dc92bcbdf9b83344` |
| https://www.monash.edu.my/study/undergraduate/pharmacy/bachelor-pharmacy | Bachelor of Pharmacy (Honours) | Matched | Unknown | not_verified | `7998a7eacb37631d97e20955a0c2aa91335734a6fcf17f90e1dcc8edcfb6340f` |
| https://www.monash.edu.my/study/undergraduate/science/bachelor-of-applied-data-science | Bachelor of Applied Data Science | Matched | S2010 | not_verified | `edac7bbcd4a0fca745ab753d5ee9afe4d9c8b84196ea0f9318cc1ba1c064784f` |
| https://www.monash.edu.my/study/undergraduate/science/bachelor-science | Bachelor of Science | Matched | Unknown | not_verified | `c6b9d7a30aa3eacc750249e1e92e11ed37fef4f503894f470ca71e07566bee5a` |
| https://www.monash.edu.my/study/undergraduate/science/bachelor-science-food-science-technology | Bachelor of Food Science and Technology | Matched | Unknown | not_verified | `60c72f206c0ea57ae802edee7c914eade9092adadd237b8f68bd778d4f75f7fc` |
| https://www.monash.edu.my/study/undergraduate/science/bachelor-science-honours | Bachelor of Science (Honours) | Matched | Unknown | not_verified | `749f1aeded939e6dd898359ea6fd7eaac8fc46096f90f25ef8fdbb535034c140` |
| https://www.monash.edu.my/study/undergraduate/science/bachelor-science-medical-bioscience | Bachelor of Medical Bioscience | Matched | Unknown | not_verified | `3d5c3815303294eea76ee7a3ec0a66d509f3d1a7e3221f7cb018acaaf92d7028` |

## 中文说明

本次只读核对了 63 个已登记课程来源、两份收费表和三个批次页面，全部返回有效 HTML。62 个课程标题与目录资格身份匹配；另一个理学硕士来源的标题含 Research，不能擅自当作完全相同的资格。学费年份为 2027，10 月名单也明确指向 2027，但名单、截止日期和学费均不能证明当前或某个批次开放申请。未知课程代码继续保留未知。以上中文是本次核对结论，不是对官网课程正文的翻译。

Production acceptance remains pending: deploy the reviewed code, allow normal indexed-source refresh, and exercise affected public flows. This read-only review does not mark the production index refreshed or close #264.
