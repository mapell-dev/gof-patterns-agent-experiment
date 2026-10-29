---
name: gof-patterns
description: Decide whether a Gang of Four design pattern is warranted before using one. Use when adding a new variant, type or behavior to object-oriented code, when code branches on a type or kind, or when a pattern such as Strategy, Factory, Decorator, Observer, Command or State is being considered.
---

# GoF patterns: when to use one, and when not to

A pattern is a cost paid now for a change expected later. Use one only when that change is real.

## Use a pattern when

- **The variation already exists or is announced.** Two or more variants exist and the requirement names more to come (for example "a new type every month"). A guess about the future does not count.
- **The variants change for different reasons or at different times**, and editing one should not risk the others.
- **Each variant needs to be tested on its own**, and the branching code makes that awkward.
- **A third case appears in the same branch.** One or two cases in a `switch` are fine; the third is the usual point to extract.

## Do not use a pattern when

- There is one variant, or a second one with no sign of a third.
- The change is temporary (a promotion, a migration, a flag that will be removed). Make it small and easy to delete.
- The pattern would add more types than the behavior it holds. An interface with one implementation, or a factory for one product, is a cost with no return.
- The language already covers it: a delegate or `Func<>` is a strategy, an `event` is an observer, a `switch` expression over a closed set is often enough.

## Common patterns, the signal, and the cheaper option

| Pattern | Signal that it pays | Try first |
|---|---|---|
| Strategy | Several interchangeable algorithms, more announced | A `switch` expression, or a `Func<>` per case |
| Factory Method / Abstract Factory | Creation varies by configuration or platform | A constructor, or a static method |
| Decorator | Behaviors stacked in different combinations at runtime | A wrapper method, or middleware the framework already has |
| Observer | Several independent listeners that come and go | A C# `event`, or a direct call when there is one listener |
| Command | Actions must be queued, logged, undone or retried | A method call |
| State | Behavior depends on a state with many transitions | A `switch` on an enum |

## Before you finish

1. Name the concrete change the pattern makes easier. If you cannot point to it in the requirement, remove the pattern.
2. Count the types you added. If there are more types than variants, say why in one line.
3. Keep the existing tests passing and add a test per new variant.
