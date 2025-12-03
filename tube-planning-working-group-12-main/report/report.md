<!-- This is a comment block in Markdown. When the document is rendered, you won't see this text.

If you need help on MarkDown syntax, you can look at the guide here: https://www.markdownguide.org/basic-syntax/.
You are also welcome to ask the Module instructors for help with writing MarkDown.

You can use this template as the starting point for your report.
Answer the questions by writing your answers in the space between the bullet points.
If you are editing this file in VSCode, you can press CTRL+K then V to open a preview of the document.

Comment blocks end by closing the "arrow" we opened at the start. -->

# Planning Tube Lines: Group Report

<!-- The headers that follow correspond to all questions in the assignment that require a written answer. 
You can write your answers in the space provided (you do not need to keep the "<" and ">" characters around the "YOUR ANSWER HERE" text).

Bear in mind that a good answer and a long answer are not necessarily the same thing!
Consider listing each point you make in a discussion as a bullet point, for example. -->

## Use of GitHub and Collaboration

<!-- In this section, you should include your [issues.png] and [pr.png] images showing how your group has used
pull requests and issues throughout the project. You should also include the URLs of one issue and one pull request that
you feel reflects your groups working practices and use of GitHub features. -->

![Caption for issues.png. If this text appears without a picture next to it, your image was not found.](issues.png)

Link to one of your group's issues: <http://link-to-an-issue-here>
<!-- NOTE: Leave the angled brackets <> around the URL to have the text stay formatted as a link -->

![Caption for pr.png. If this text appears without a picture next to it, your image was not found.](pr.png)

Link to one of your group's issues: <http://link-to-a-pull-request-here>

Link to one of your group's pull requests: <http://link-to-a-pull-request-here>
<!-- NOTE: Leave the angled brackets <> around the URL to have the text stay formatted as a link -->

## Adding Additional Flow

1. What benefit does using the `send_flow_along` method provide when working with the `Flow` class, over manipulating the `flow_matrix` directly?

YOUR ANSWER HERE

2. What is the reason for the check, in the case of the `path` having at least two elements?

YOUR ANSWER HERE

3. Suppose I have some fixed size `n`, sources `sources`, and sinks `sinks`.
   Suppose that I have also created a path `p`, which starts and ends at both a source and sink node (`p[0]` and `p[-1]` are **both** in `sources` and `sinks`).
   Suppose I have also fixed an amount `a`.
   Consider the following code snippet:

   ```python
   reverse_p = list(reversed(p))
   minus_a = -a

   ZF = Flow.zero_flow(n, sources, sinks)
   ZF.send_flow_along(p, a)
   ZF0 = ZF.flow_matrix.copy()

   ZF = Flow.zero_flow(n, sources, sinks)
   ZF.send_flow_along(p, minus_a)
   ZF1 = ZF.flow_matrix.copy()

   ZF = Flow.zero_flow(n, sources, sinks)
   ZF.send_flow_along(reverse_p, a)
   ZF2 = ZF.flow_matrix.copy()

   ZF = Flow.zero_flow(n, sources, sinks)
   ZF.send_flow_along(reverse_p, minus_a)
   ZF3 = ZF.flow_matrix.copy()
   ```

- What would be the difference between `ZF0` and `ZF1`?

YOUR ANSWER HERE

- What would be the difference between `ZF0` and `ZF2`?

YOUR ANSWER HERE

- What would be the difference between `ZF0` and `ZF3`?

YOUR ANSWER HERE

## Finding Paths via BFS

1. The description of the BFS algorithm introduces both a list of visited nodes, and also requires us to keep track of the previous node in the path for each node.
  Whilst conceptually these are different things, do you need to treat them as separate entities when implementing the BFS algorithm in your code?

YOUR ANSWER HERE

2. `path_from_bfs` is not given the root node as an explicit argument.
  Can the method determine the root node from the `path_trace`, and if so, how?

YOUR ANSWER HERE

## The Edmonds-Karp Algorithm

1. What the purpose of the `maxiter` input argument is, both in terms of code functionality and code design / safety.

YOUR ANSWER HERE

2. Describe at least 2 distinct problems you identified with the readability of the `edmonds_karp` function, and what you did to address them when you implemented the `Network.edmonds_karp` method.

YOUR ANSWER HERE

3. What measures (if any) did you take to ensure your `Network.edmonds_karp` method retained identical behaviour to the original `edmonds_karp` function that you were provided?

YOUR ANSWER HERE

## Solving Flow Problems

1. We are told to throw an error in `maximum_flow` if a node appears in both `sources` and `sinks`.
   We do not do this in `sufficient_flow`, when `sources.keys()` and `sinks.keys()` may contain the same node.
   Why is this?

YOUR ANSWER HERE

## Sending Queries to the Web Service

1. What benefits to the codebase does having the `send_query` function provide?
   Provide at least one benefit.

YOUR ANSWER HERE

## Identifying the `Criteria` Design Pattern

1. What is the purpose of the `to_json_part` method in each of the `Criteria`, `CostCriteria`, and `PerformanceCriteria`?
   Why is it implemented for the two subclasses (`CostCriteria`, and `PerformanceCriteria`) as well as the base `Criteria` class?

YOUR ANSWER HERE

2. How are `Criteria`, `CostCriteria`, and `PerformanceCriteria` compared when the `==` Python comparison operator?

YOUR ANSWER HERE

3. Why does the `Criteria` class have both a `evaluate` and `_evaluate` method?

YOUR ANSWER HERE

4. Regarding the `Criteria`, `CostCriteria`, and `PerformanceCriteria` classes, which [behavioural pattern](https://refactoring.guru/design-patterns) are TFL following in the design of this code?
   Justify your answer by matching the `Criteria`, `CostCriteria`, and `PerformanceCriteria` classes  (or the appropriate method of these classes) to the roles defined in the behavioural pattern you identify.

YOUR ANSWER HERE

## Writing the `_evaluate` Methods

1. Why does `PerformanceCriteria._evaluate` need to take `*args` and `**k**wargs`, even though they are not used in the method?

YOUR ANSWER HERE

2. Despite having written the `Proposal` class, we are not enforcing the `proposal` argument to the `_evaluate` (or even the `.evaluate`) methods to be `Proposals`, only requiring that they be `Network`s.
   Why is this?

YOUR ANSWER HERE

## Saving and Loading `CriteriaGroup`s

1. During testing, do you notice any odd behaviours when loading a `.cfile`, and then saving the resulting `CriteriaGroup` back to a `.cfile`  via `to_criteria_file`?
   If you do, provide examples of these behaviours and provide an explanation for them.

YOUR ANSWER HERE

2. In light of your answer to part 1, do you think the docstring provided for `to_criteria_file` is suitable for describing what the method is doing?
   Make suitable edits that rectify the docstring, if you argue that it is inadequate.

YOUR ANSWER HERE

## Time Spent (Edmonds-)Karp Fishing

1. What is the purpose of using the networks $G_{N, \delta}$ for investigating the scaling of of $t_{exe}$, as opposed to using (a sub-network of) the TFL network that we have available?

YOUR ANSWER HERE

2. Based on the information contained in your plots, comment on (and / or qualify and quantify) the relationship between $t_{exe}$, $\vert V_{N, \delta}\vert$, and $\vert E_{N, \delta}\vert$.
   Any conclusions you draw should be backed up by evidence or data from your plot.

![This line will include your plot as an image in your report, provided it is saved to the repository in the same folder as report.md.](./edmonds-karp-exe-times.png)

## Designing A Line

1. How would you adapt the `ucl-line.py` script into an integration (or unit) test for your package?
   You should mention anything you would change regarding the inputs to the script, the files it depends on, and how it runs.
   You should also discuss any generalisations that would (or could) be made to the script to accommodate this change to a test.
   Optionally, you can implement such a test in your package directly in support of your answer to this question - if you choose to do this you give the name of the file and test function that contains the test below.

YOUR ANSWER HERE

## The Best Proposal

1. Paste the text output (containing the rankings of the proposals) from your script into this document.
   You can use a `csv`-formatted block to ensure the text rendering displays appropriately.

```csv
YOUR OUTPUT HERE
```

2. Based on your analysis in this script, which proposal would you recommend to TFL if they are planning to start construction in July?

YOUR ANSWER HERE
