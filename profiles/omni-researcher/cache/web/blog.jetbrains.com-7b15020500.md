# Understanding AI’s Impact on Developer Workflows

AI coding assistants are no longer shiny add‑ons: they are standard parts of our daily workflows. [We know](https://www.sciencedirect.com/science/article/abs/pii/S0950584924002155) developers’ perspectives on them in the short term, and [many say](https://blog.jetbrains.com/research/2025/10/state-of-developer-ecosystem-2025/) they get more done and spend less time on boilerplate or boring tasks. But we know far less about what happens over years of real work in real projects – and whether what developers perceive has changed in the workflow has actually changed.

There are already a number of studies on developer-AI interaction, but the existing research is often limited in scale or depth, and the studies are rarely long-term investigations. Our [Human-AI Experience](https://jb.gg/hax) team (HAX) was interested in developers’ experience with AI tools over a long period of time, so they analyzed two years of log data from 800 software developers. They also wanted to analyze self-reported perceptions and compare them with the objective data, so they conducted a survey and follow-up interviews.

Here we present our findings from our HAX team’s mixed-method [study](https://jb.gg/j2rrsg), which our team is presenting this week at [ICSE 2026](https://conf.researchr.org/home/icse-2026) in Rio de Janeiro.

The study demonstrates how developers’ workflows have evolved with AI tools. A major takeaway from the study is that AI redistributes and reshapes developers’ workflows in ways that often elude their own perceptions.

In this blog post, we:

- Present our methodology for the study, namely:
 - Log data from a two-year period
 - Survey and interview responses
- Describe the components of developer workflows, including relevant previous research.
- Discuss the results of our mixed-methods study.

## Analyzing how developers are evolving their workflows with AI tools

In this section, we will describe how we set up the HAX [study](https://jb.gg/j2rrsg), investigating both how developers behave (using log data) and what developers perceive (through interviews).

A major advantage of this design is that the methods compensate for each other’s blind spots. Logs can show that workflows are changing, but not why; self-reports can explain motivations and context, but they are biased and often miss subtle behavioral shifts. By triangulating across both, mixed methods make it easier to spot gaps between perception and practice and to build a more complete, grounded picture of how AI is reshaping everyday development work.

### Telemetry in research

Telemetry is a well-established method for gathering data, in use since at least the 1800s. The word itself comes from the Greek for ‘far’ (tele) and ‘measure’ (metron), and it usually refers to data collected remotely. Its use enables more accurate experiments and better observability without constant manual measurement.

For example, telemetry is useful in healthcare settings for measuring blood pressure, heart rate, and oxygen levels over extended periods. In research, it can be used to capture continuous, real‑time data (for example, physiological, environmental, or system-performance signals) and send it to a central system for monitoring and analysis.

In the context of our research, telemetry is the stream of fine-grained, anonymized events that IDEs automatically record as developers work: which actions they take, when they take them, and in what sequence. That is, it collects information like the number of characters typed (not the actual characters), debugging sessions started, code deletions, paste operations, and window focus changes. If you’re interested, see our [Product Data Collection and Usage Notice](https://www.jetbrains.com/legal/docs/terms/product_data_collection/#detailed-data-collection) for further details.

We know from previous studies that telemetry can indeed uncover interesting patterns in developers’ behavior. For example, [these researchers](https://ieeexplore.ieee.org/document/7181430) found that developers actually spend a good chunk (70%) of their time on comprehension activities like reading, navigating, and reviewing source code.

### How developers behave: Investigating log data from a two-year period

For this study, telemetry served as a behavioral lens on developer workflows. Instead of asking developers how they think AI assistants affect their workflows, we looked at what actually happens in the editor over a span of two years: how much code is written, how often code is edited or undone, when external snippets are inserted, and how frequently developers switch back into the IDE from other tools. By aggregating and comparing these signals for AI users and non‑users, telemetry made it possible to observe subtle, long-term shifts in everyday practice that would be hard to capture through surveys or controlled lab tasks alone.

More specifically, our team worked with anonymized usage logs from several JetBrains IDEs, including IntelliJ IDEA, PyCharm, PhpStorm, and WebStorm. We filtered down to devices that were active in both October 2022 and October 2024 so the same developers could be tracked over a full two-year window. Note that the first date (October 2022) was chosen because that was when ChatGPT was first released.

From there, we built two groups: 400 ******AI users******, whose devices interacted with JetBrains AI Assistant at least once a month from April to October 2024, and 400 ******AI non-users******, whose devices never used the assistant during the study period. The reasoning behind checking for use from April 2024 was that at that point, AI assistants had become widely available and stable in IDEs; we also wanted to ensure that the users really had integrated AI assistants into their workflows.

As the telemetry logs are by nature complex, our team picked out well-defined events, i.e. user actions, to represent each of the workflow dimensions which are described in more detail below. These are:

1. Typed characters – **productivity**
2. Debugging session starts – **code quality**
3. Delete and undo actions – **code editing**
4. External paste events without an in-IDE copy – **code reuse**
5. IDE window activations – **context switching**
Of course, any chosen proxy would have its limitations, and our chosen metrics do as well. That being said, our goal with this study was to detect patterns of change in developer workflows over time and not to identify causal effects.

By aggregating these metrics per user per month, we could see how each dimension evolved over time for AI users versus non-users, focusing on patterns of change. Overall, our dataset comprised 151,904,543 logged events performed by the 800 users.

Our data processing involved computing the total number of occurrences per device per month. This means we had a clear, high-level dataset of monthly counts for every action, which is ideal for tracking activity and identifying meaningful behavioral trends.

### What developers perceive: Qualitative insights from surveys and interviews

To balance the behavioral view with developers’ own perspectives, our team also ran an online survey aimed at professional developers. We framed the questions around the same workflow dimensions, asking how they felt AI assistants had affected their productivity, code quality, editing habits, reuse patterns, and context switching. In total, 62 developers completed the survey, giving us a broad picture of perceived benefits, drawbacks, and changes since they started using AI tools.

The details of the survey can be found in §3.1 of the [paper](https://jb.gg/j2rrsg), as well as in the supplementary [materials](https://zenodo.org/records/18220544). In addition to demographic questions, the survey included:

1. Scale questions about overall experience and reliance on AI tools for coding
2. Scale questions on developer perception, specific to the workflow dimensions
3. Open-ended question asking for a specific example of workflow impact and AI tools for coding
The first two types of questions (items 1 and 2) were constructed as 5-point scales, where the participants were asked to provide a rating, indicating the degree to which they agreed or disagreed with a statement. In our survey, the scale concerned the degree of change: with (1) being *significantly decreased* and (5) *significantly increased*.

The questions from item 2 can be summarized as follows:

- For **productivity**, we asked directly about overall productivity and also about time spent coding.
- For **code quality**, we asked directly about the quality of code and also about code readability.
- For **code editing**, we asked about the frequency of editing or modifying their own code.
- For **code reuse**, we asked about the frequency of use of code from external sources, e.g. libraries, online examples, or AI-suggested code.
- For **context switching**, we asked directly about the frequency of context switching – switching between different tasks or thought processes.
After the survey, our team invited a smaller group of participants to short, semi-structured interviews. In those conversations, we dug deeper into how they actually use AI day to day: when they reach for it, how they decide whether to trust a suggestion, and whether their work feels more or less fragmented now. Those qualitative stories helped us interpret the telemetry curves: for example, understanding why someone might report “not much has changed” even when their logs show big shifts in how much they type, delete, or paste external code.

## Dimensions of the developer workflow

To understand the developer workflows better, our HAX [study](https://jb.gg/j2rrsg) divided the areas of interest into the following dimensions, mentioned above:

1. Productivity
2. Code quality
3. Code editing
4. Code reuse
5. Context switching
**Productivity** captures the most intuitive question people ask about AI tools: Do they help developers get more done? This dimension sets the stage by asking whether AI-assisted workflows are simply faster at producing code, and how that plays out over time compared to developers who do not use AI at all.

And although the impact of LLM-based coding tools on developer productivity has been a subject of many studies, there is not yet a clear picture of how – or whether – AI assistance really has a positive impact on developers’ productivity. On top of that, researchers use various measures (e.g. characters typed, tasks completed, completion requests accepted). Interestingly, this [study](https://arxiv.org/pdf/2205.06537) observed that developers perceived their productivity as increasing with Copilot despite the data showing otherwise. Another [study](https://arxiv.org/pdf/2507.09089) had similar findings: even though developers thought that their completion time of repository issues improved by 20%, the numbers actually show that they were 19% slower at completing tasks. In our study, we chose to measure code quantity.

**Code quality** shifts the focus from “how much code is written” to “how well the code is written.” Rather than inspecting code directly, this dimension looks at how often developers enter debugging workflows as a behavioral signal of running into problems or uncertainty. It introduces the idea that AI might change not only the number of issues that surface, but also how and when developers choose to investigate them, offering a window into how confident they feel about the code that ends up in their projects. Researchers in this [study](https://arxiv.org/pdf/2210.14306) observed that developers spend more than a third of their time double-checking and editing Copilot suggestions.

**Code editing** looks at what happens after the first draft: how frequently code is reshaped, corrected, or thrown away. Here, the interest is in how much developers are editing, undoing, and deleting – as a way of understanding whether AI turns programming into a more iterative, high‑revision activity. This dimension helps illuminate the “curation” side of AI use: accepting suggestions, reworking them, and deciding what ultimately stays in the codebase. This [study](https://ieeexplore.ieee.org/document/10764992) looked not at the time spent editing, but how much is deleted or reworked: of the code that is at first accepted, almost a fifth is later deleted, and about 7% is heavily rewritten.

Developers have always reused code (e.g. from libraries, internal snippets, Stack Overflow), but AI assistants introduce a new, often opaque channel for bringing external code into a project. **Code reuse** as a workflow dimension zooms out to ask where code comes from in the first place. We know from previous studies like this [one](http://one) that AI assistants provide boilerplate code and suggest commonly used patterns or snippets derived from training data. This dimension focuses on how often developers appear to integrate code from outside the current file or project, framing AI as part of a broader shift in reuse practices rather than an isolated feature.

Modern development work already involves frequent jumping between integrated development environments (IDEs), browsers, terminals, and communication tools, and AI assistants promise to streamline some of this jumping by keeping more help inside the editor. **Context switching** widens the lens from code to attention. This dimension asks whether that promise holds in practice, or whether AI ends up reshaping – rather than simply reducing – the ways developers move their focus across tools and tasks during everyday work.

For one, this [study](https://dl.acm.org/doi/10.1145/3661145) has shown that interacting with AI assistants can add cognitive overhead and fragment tasks, as developers alternate between writing code, interpreting suggestions, and managing the dialogue with the system. This raises an open question: are these tools actually reducing context switching overall, or mostly trading one form of interruption for another?

## Two lenses on AI-assisted workflows

By combining different methods, our study is able to deliver a more complete picture of how AI coding tools change (or don’t change) developers’ workflows. We also learned that behavioral changes are largely invisible to the developers themselves. Together, these patterns sketch out what it really means to evolve with AI in a modern IDE.

In this section, we walk you through the results, presenting them by dimension. The table below displays an overview of our results.

![Understanding AI's Impact on Developer Workflows](https://blog.jetbrains.com/wp-content/uploads/2026/04/evolving-ai_table-results.png)

### Productivity

The first dimension of our study looked at how AI assistants affect productivity, measured in the telemetry part as how much code developers type over time and in the survey as how the developers perceived their productivity and time spent coding. Here, both the actual behavior and perception are aligned: with an in-IDE AI assistant, developers are writing more code.

In the graph below, the average number of typed characters is displayed for the **AI users** and **AI non-users** for the investigated time period. Shaded regions represent a ±1 deviation from the mean.

![Understanding AI's Impact on Developer Workflows](https://blog.jetbrains.com/wp-content/uploads/2026/04/rq1_logs.png)
From the graph above, it is clear that **developers who adopted the in‑IDE AI assistant consistently typed more characters** than those who never used it, and this gap grew over the two‑year period. The log data revealed the trend that ****AI users**** increased the number of characters typed by almost 600 per month, in contrast to ****AI non-users****, who only displayed an average increase of 75 characters per month. This data suggests that the difference is not just a one‑off spike; it’s a sustained shift in developer behavior.

Survey respondents (all ****AI users****) similarly experienced an increase in productivity. Over 80% of respondents reported that the introduction of AI coding tools slightly or significantly increased their productivity, while two respondents said that it slightly or significantly decreased it. Regarding time spent coding, more than half said that their coding time decreased, while about 15% indicated that it increased.

Interview participants largely echo this in their own words. For example, one developer (3–5 years of experience and a regular AI user) said:

> When I get stuck on naming or documentation, I immediately turn to AI, and it really helps.

In this dimension, both the perception and actual behavior are similar. These results demonstrate that **developers are producing more code in the editor and perceive a productivity increase with AI tools**.

### Code quality

For code quality, the study uses a simple behavioral signal: how often developers start a debugging session in the IDE. This is not a perfect measure of “good” or “bad” code, but it does tell us how frequently people feel the need to step through their program to understand or fix something. In this dimension, the developers’ behavior and perception are not aligned, at least not in a statistically significant way: there is no change in AI users’ debugging behavior, but a slight improvement in perception of code quality and readability.

In the graph below, the average number of started debugging instances is displayed for the ****AI users**** and ****AI non-users**** for the investigated time period. As before, shaded regions represent a ±1 deviation from the mean. Across the two years, both AI users and non‑users show active debugging behavior, and the differences between the groups are much less dramatic than for the productivity measure.

![Understanding AI's Impact on Developer Workflows](https://blog.jetbrains.com/wp-content/uploads/2026/04/rq2_logs.png)
The above graph shows the average number of debugging instances per month for each group as two lines that sit close together. Our statistical analysis told us that for ****AI users****, there was no significant change in behavior over time. For ****AI non-users****, there was a slight decrease in debugging starts in the time period.

Most survey respondents say using AI coding tools has somewhat positively changed their code quality. Namely, when asked whether the quality of their code increased because of using AI coding tools, almost half say that it slightly or significantly increased, while about 10% say that it slightly or significantly decreased. For the readability of the code, the respective numbers are 43.5% and 6.5%, though 50% indicate that they did not observe a change.

Despite this improvement with AI, some developers still do not completely trust AI-generated code. For example, a developer with 3–5 years of experience reported in the interview:

> I triple-check it, and even then, I still feel a bit uneasy.

For this dimension, our results show us that although **developers report an increase in code quality from their point of view**, their behavior (in the proxy we chose to analyze) does not show a change for AI users.

### Code editing

When we look at code editing, the difference between behavior and perception is more striking: while the developers reported little change, the log data showed a stark rise in their behavior over time. Here, the telemetry value was how often developers delete or undo code, and in the survey, they were asked whether they thought they edited their own code more with AI tools.

In the graph below, the average number of deletions is displayed for the ********AI users******** and **AI non-users** for the investigated time period. As before, shaded regions represent a ±1 deviation from the mean. Across the two years, the trend lines show a big difference between AI users and non‑users.

![Understanding AI's Impact on Developer Workflows](https://blog.jetbrains.com/wp-content/uploads/2026/04/rq3_logs.png)
The ****AI users****’ line sits noticeably higher, with a statistically significant increase of about 100 deletions per month. In contrast, ****AI non-users**** increased their deletions in the same period, on average, only about 7 times per month. This data suggests more frequent editing and rework when AI is helping to generate code.

In the qualitative data, the developers do not report seeing such a big change. Half of the respondents reported no perceived change in their code-editing behavior since adopting AI tools; about 40% reported a slight or significant increase, and about 7% reported a decrease. A system architect with more than 15 years of coding experience said:

> AI is like a second pair of eyes, offering pair programming benefits without social pressure – especially helpful for neurodivergent people. It’s not always watching, but I can call on it for code review and feedback when needed.

Compared to the previous dimension of code quality, developers’ perception and actual behavior with respect to code editing are inverted. Namely, they do not perceive a significant change in how much they are editing code, but **the log data shows a large increase for developers who have adopted AI assistance**.

### Code reuse

For code reuse, the study looked at how often developers paste content into the IDE that does not come from a copy action inside the same IDE session. The results for this dimension are less divergent, both between AI users vs. non-users and between perception vs. behavior.

In the graph below, the average number of external pastes is displayed for the ****AI users**** and ****AI non-users**** for the investigated time period. As before, shaded regions represent a ±1 deviation from the mean. Across the two years, the trend lines do not show a big change for either AI users or non‑users.

![Understanding AI's Impact on Developer Workflows](https://blog.jetbrains.com/wp-content/uploads/2026/04/rq4_logs.png)
The trend line for ****AI users**** is higher overall than for ****AI non-users****, indicating that they reuse external code more frequently. However, there is not a large change over time for either group.

The responses from the survey and interview don’t show a clear pattern either. In the survey, about a third of respondents said they perceived that their use of code from external sources slightly or significantly increased with the adoption of AI tools, while a fifth reported it decreased; 44% observed no change.

From previous studies, we might have expected that developers using AI tools are more likely to reuse external code. In contrast, they report a different picture. For example, a developer with over 15 years of experience says:

> For me, it’s better to take responsibility for what I did myself rather than adopt a third-party solution.

### Context switching

The last dimension we studied is context switching, or how often developers jump back into the IDE after working in another window, such as a browser. AI tools, especially in-IDE ones, are often marketed as a way to keep developers “in flow” by reducing the need to leave the editor for help. Although the qualitative data does not show a pattern in either direction, the telemetry tells a more complicated story: over time, AI users actually show more IDE activations than non‑users, meaning they are switching contexts at least as much, if not more.

In the graph below, the average number of IDE activations is displayed for the **AI users** and ****AI non-users**** for the investigated time period. As before, shaded regions represent a ±1 deviation from the mean. Across the two years, the trend lines do show a slight increase for ****AI users****.

![Understanding AI's Impact on Developer Workflows](https://blog.jetbrains.com/wp-content/uploads/2026/04/rq5_logs.png)
Like for the previous dimension, the trend line for **AI users** overall sits higher. However, here the trends diverge: **AI users** show an increase of about 6 IDE activations per month, while **AI non-users** show the opposite, a decrease of about 7 per month.

In contrast to the differences seen in the log data, the survey responses were less suggestive of a clear pattern. Namely, about a quarter of respondents indicated an increase, about a fifth a decrease, and about half no change.

In the interviews, developers indicate that using AI tools does not result in a simple drop in context switching, but a different pattern of fragmentation. One developer said:

> I stopped switching contexts, saving a few seconds every time I would have googled something.

In this workflow dimension, we have seen a similar pattern as before: there was **a slight increase in the log data for AI users**, but no clear pattern in the qualitative data. This suggests that even with in-IDE AI assistance, developers are still switching contexts, sometimes even more than those not using AI assistance.

## AI’s impact on effort and attention

Taken together, the results of our HAX [study](https://jb.gg/j2rrsg) suggest that AI coding assistants are quietly reshaping developer workflows in ways that otherwise can go unnoticed. That is, our study shows that these shifts are subtle enough that developers don’t always see them clearly in their own habits. That’s why combining methods in investigations, like telemetry with surveys and interviews, matters: it reveals the gap between what feels different and what actually changes in day‑to‑day behavior.

If you’re building or adopting AI tools, the takeaway is simple: don’t just ask whether people like them. You should look closely at what they are actually doing!

#### Subscribe to JetBrains Research blog updates

## Discover more