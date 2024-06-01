# Latest AI News
## News Item
- URL: https://x.com/JamesAlcorn94/status/1794897317503631394
- Content:
SWE-agent is a stunning paper. Not for of its results on swe-bench, but for so concretely demonstrating the idea that (1) llm agents equipped with llm-native interfaces are the future and; (2) by implication, there are a whole lotta interfaces to redesign.
@jyangballin
 & co set out to build an autonomous software engineer with LLMs. Not a new idea per se. The difference is in the approach: they design an agent-computer interface ('ACI') through which the LLM can interact with the codebase, in lieu of using existing HCIs like the Linux shell.  

Why? Because existing interfaces, like GUI-based IDEs, have "rich visual components and feedback that make them powerful tools for humans, but [unsuitable] for LMs." 

Put another way, LLMs & humans are fundamentally different user constituencies, and forcing an LLM to use *our* interfaces is shaping up to be a really bad idea. 

The authors observe that, when using the popular vim text editor, the agent wastes time & precious context window verifying minor results that a human wouldn't (e.g. file removal). vim has a catastrophic impact on agent performance; the reasons it's a great product for humans are the exact same reasons it's a terrible product for llms. 

This won't be a controversial idea, but it's not yet widely appreciated. IMO, most novel ACIs will be designed in-house at startups for the next year or two - i.e. llm application devs will build internally the ACI necessary for their agent's use case, be it in observability (perhaps an ACI for the APM stack), security (ditto for SIEM), or whatever use case they're building around. 

If the idea takes hold, new startup opportunities around ACIs could resemble those of the API ecosystem, to begin with - design, testing, security, governance. But this could get pretty cooked, pretty quick: Not hard to imagine a future where we ask an agent to design and implement its own interfaces, in real time, and in turn instruct another agent to limit what agent #1 can retrieve from our system. Unclear where the value accrues in this scenario.
- Summary:
SWE-agent is a paper that highlights the importance of designing llm-native interfaces for autonomous software engineers. Existing interfaces designed for humans are not suitable for LLMs, as demonstrated by the inefficiencies observed with the popular vim text editor. The future may involve startups creating custom ACIs for their specific agent use cases, leading to potential new opportunities in the startup ecosystem. The concept of agents designing and implementing their own interfaces in real time raises questions about where the value lies in this scenario.

## News Item
- URL: https://x.com/myfear/status/1795549367580950814
- Content:
chatgpt-system-prompts: A concise collection of leaked system prompts that reveal the complex behaviors behind the responses of ChatGPT4 and GPTs with action APIs. https://bit.ly/3OQc9a0
#chatgpt
GitHub - Ed0ard/chatgpt-system-prompts: A concise collection of leaked system prompts that reveal...
From github.com
- Summary:
A concise collection of leaked system prompts that reveal the complex behaviors behind the responses of ChatGPT4 and GPTs with action APIs. GitHub link: https://bit.ly/3OQc9a0
#chatgpt

## News Item
- URL: https://x.com/emollick/status/1795515457228935658
- Content:
You are both early (47% of Americans say they have never even heard of ChatGPT) and also surprisingly on time (I would not have expected that 7% of Americans are already using ChatGPT daily, and almost 1 in 5 Americans use an LLM at least weekly)

Survey: https://reutersinstitute.politics.ox.ac.uk/sites/default/files/2024-05/Fletcher_and_Nielsen_Generative_AI_and_News_Audiences.pdf...
- Summary:
Key points extracted from the tweet content:
- 47% of Americans have never heard of ChatGPT
- 7% of Americans are already using ChatGPT daily
- Almost 1 in 5 Americans use an LLM at least weekly

Survey: https://reutersinstitute.politics.ox.ac.uk/sites/default/files/2024-05/Fletcher_and_Nielsen_Generative_AI_and_News_Audiences.pdf...

## Meeting Agenda
- [SWE-agent is a paper that highlights the importance of designing llm-native interfaces for autonomous software engineers. Existing interfaces designed for humans are not suitable for LLMs, as demonstrated by the inefficiencies observed with the popular vim text editor. The future may involve startups creating custom ACIs for their specific agent use cases, leading to potential new opportunities in the startup ecosystem. The concept of agents designing and implementing their own interfaces in real time raises questions about where the value lies in this scenario.](https://x.com/JamesAlcorn94/status/1794897317503631394)
- [A concise collection of leaked system prompts that reveal the complex behaviors behind the responses of ChatGPT4 and GPTs with action APIs. GitHub link: https://bit.ly/3OQc9a0](https://x.com/myfear/status/1795549367580950814)
- Key points extracted from the tweet content:
  - 47% of Americans have never heard of ChatGPT
  - 7% of Americans are already using ChatGPT daily
  - Almost 1 in 5 Americans use an LLM at least weekly
  - [Survey link](https://reutersinstitute.politics.ox.ac.uk/sites/default/files/2024-05/Fletcher_and_Nielsen_Generative_AI_and_News_Audiences.pdf...)