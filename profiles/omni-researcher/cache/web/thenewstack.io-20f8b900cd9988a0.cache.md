# Beyond the Commit: Developer Perspectives on Productivity with AI Coding Assistants
## 1. Introduction
One salient and increasingly common use case of AI tools in practice is that of coding assistants, with prominent examples including GitHub Copilot and Cursor.
As these systems are integrated into real-world software development workflows, a natural question arises: how can we measure their impact on developer productivity?
Indeed, AI coding assistants that substantially boost productivity could necessitate a rethinking of how software is developed in the age of AI ( Peng et al., 2023 ) .

...

We deploy the Developer Experience (DX) survey framework ( Greiler et al., 2022 ) across the company to collect perceptions of productivity with AI coding assistants, focusing on two core questions: developers’ satisfaction with AI tools and their perceived time savings.

...

## 2. Related Work
### Background on productivity in software engineering.
Complementing these perspectives, new telemetry-driven metrics such as Diff Authoring Time (DAT) provide fine-grained signals of developer effort at scale ( Beller et al., 2025 ) .

...

#### Measuring productivity with AI coding assistants.
The adoption of AI coding assistants has risen sharply in recent years, with tools such as GitHub Copilot and Cursor now integrated into major IDEs and workflows used by millions of developers ( GitHub, 2023 ) .

...

For example, Weisz et al. (2022) found that different users benefited to varying degrees when using AI coding assistants. Ziegler et al. (2024) found that developers who used GitHub Copilot reported higher productivity levels.

...

## 3. Research Design
### 3.2. Interview
|Seniority |Developer Role |Department Function |
| --- | --- | --- | --- |
|P1 |Early Career |Backend Dev |Customer Products |
|P2 |Mid Career |Full stack Dev |Platform Engineering |
|P3 |Mid Career |Full stack Dev |Data |
|P4 |Early Career |Backend Dev |Customer Products |

...

#### Participants.
##### Protocol.
We conducted 11 semi-structured interviews led by the first author. The interviews were conducted virtually via Teams, lasting between 30 and 45 minutes each.
The interview content covered topics around the participants’ engineering and AI background, use cases of GitHub Copilot, and perceptions on productivity metrics.

...

## 4. Results
### 4.3. RQ3: How do AI productivity metrics impact the workflow?
#### 4.3.1. Use Case 1: Implementing new features (P1,2,3,6,8,11).
One of the predominant use cases of GitHub Copilot is to write code to implement new features ( Peng et al., 2023 ) .
Interviewees described how AI can easily provide multiple implementations and “turn out far more lines of code” than a human developer can (P6).

...

Interviewees discussed how using GitHub Copilot may improve certain factors in the shorter term—e.g., reduce frustration and cognitive load ( Factor 2 ) and development time ( Factor 3 ), but expressed concern about junior developers over-relying on GitHub Copilot at the

...

Table 2. We identify 6 factors impacting developer productivity with AI coding assistants that span short- to long-term dimensions. Based on participant quotes, we curate questions to facilitate future evaluations of each factor.

...

• To what extent does AI reduce context-switching between tools (e.g., docs, Stack Overflow, Google)? • How confident are developers in relying solely on AI suggestions for everyday work?

...

• Do developers feel AI frees up time for more creative or higher-value work? | (5)Technical expertise: • Do junior engineers over-rely on AI, and how does this affect onboarding or learning? • Are developers at risk of skill decay due to continued AI usage?

...

| (6) Ownership of work: • Do developers maintain a deep understanding of codebases when AI contributes significantly? • Does AI affect perceived authorship, accountability, and willingness to maintain code?

...

## References
A large-scale survey on the usability of ai programming assistants: Successes and challenges. In _Proceedings of the 46th IEEE/ACM international conference on software engineering_ . 1–13.
* Liu et al . (2024) Chao Liu, Xindong Zhang, Hongyu Zhang, Zhiyuan Wan, Zhan Huang, and Meng Yan. 2024.

...

(2024) Irina Mariasova, Yanina Ledovaya, Olga Lvova, and Mikhail Bogdanov. 2024.
_Developers save up to 8 hours per week with JetBrains AI Assistant_
. JetBrains AI Blog.
https://blog.jetbrains.com/ai/2024/04/developers-save-up-to-8-hours-per-week-with-jetbrains-ai-assistant/

...

Software Developers’ Perceptions of Productivity. In _Proceedings of the ACM SIGSOFT International Symposium on Foundations of Software Engineering_ . 192–203.
* Mozannar et al . (2024a) Hussein Mozannar, Gagan Bansal, Adam Fourney, and Eric Horvitz. 2024a. Modeling User Behavior and Costs in AI-Assisted Programming.

...

(2023) Atsushi Shirafuji, Yusuke Oda, Jun Suzuki, Makoto Morishita, and Yutaka Watanobe. 2023. Refactoring programs using large language models with few-shot examples. In _2023 30th Asia-Pacific Software Engineering Conference (APSEC)_ . IEEE, 151–160.
* Song et al . (2024) Fangchen Song, Ashish Agarwal, and Wen Wen. 2024.