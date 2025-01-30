To improve the system and the task prompt so it classifies reviews only with
the matching topics that are explicitly stated in the review, you can focus on
the following key aspects:

---

### 1. **Refine the Task Prompt for Precision**  
Explicitly emphasize in the prompt that the output should **strictly match
topics explicitly mentioned in the text**, avoiding any inferred or implied
topics. For example:

**Refined Prompt:**  
You are a classification system. Your task is to assign a topic from a
predefined list to a provided text. The topic must be explicitly mentioned or
clearly described in the text. Avoid assigning topics based on assumptions or
implications.  

**Input:**  
Text: [Insert text here]  
Topics: [Insert list of topics here]  

**Output:**  
The single topic from the list that is explicitly mentioned in the text.  

---

### 2. **Incorporate "No Match" Handling**  
Some reviews may not explicitly align with any provided topic. To handle this
case, include a fallback option like **"No Match"** or **"Uncategorized"** to
ensure the system doesn't force a topic when none is present. For example:

**Refined Example:**  
**Input:**  
Text: "The customer service team was unhelpful when resolving my issue."  
Topics: Gameplay, Graphics, Story, Multiplayer, Bugs, Performance Issues  

**Output:**  
No Match  

---

### 3. **Add More Nuanced Examples**  
Provide examples of both **matching** and **non-matching** scenarios to better
guide the system. Examples should clearly differentiate between text that
explicitly mentions a topic and text that does not.  

**Examples:**  

1.  
**Input:**  
Text: "The graphics and sound design in this game are breathtaking."  
Topics: Gameplay, Graphics, Story, Multiplayer, Bugs, Performance Issues  

**Output:**  
Graphics  

2.  
**Input:**  
Text: "The game frequently crashes when I try to load a save file."  
Topics: Gameplay, Graphics, Story, Multiplayer, Bugs, Performance Issues  

**Output:**  
Bugs  

3.  
**Input:**  
Text: "I love how this game encourages you to experiment with different
strategies."  
Topics: Gameplay, Graphics, Story, Multiplayer, Bugs, Performance Issues  

**Output:**  
Gameplay  

4.  
**Input:**  
Text: "The price of the game is too high for what it offers."  
Topics: Gameplay, Graphics, Story, Multiplayer, Bugs, Performance Issues  

**Output:**  
No Match  

---

### 4. **Break Down Text for Topic Matching**  
If the review contains multiple sentences, guide the system to evaluate each
part independently and match topics accordingly. You can update the prompt to
include instructions for analyzing sentences individually:

**Updated Prompt:**  
Analyze the provided text sentence by sentence. Assign a topic from the
predefined list only if the topic is explicitly stated or clearly described in
the text. If no topic matches, return "No Match."  

---

### 5. **Add a Confidence Mechanism (Optional)**  
Introduce a confidence threshold that ensures topics are assigned only when
there is a high level of certainty. For example:

- If the system has doubts or low confidence in the explicit match, it should
  default to "No Match."  

---

### 6. **Include Multi-Topic Classification (Optional Extension)**  
If a single review could explicitly mention multiple topics, adjust the system
to allow for multi-topic classification. Update the examples to show how to
handle such cases:

**Example:**  
**Input:**  
Text: "The game has stunning graphics, but the multiplayer servers keep
crashing."  
Topics: Gameplay, Graphics, Story, Multiplayer, Bugs, Performance Issues  

**Output:**  
Graphics, Multiplayer  

---

### Final Refined Prompt with Examples  

**Prompt:**  
You are a classification system. Your task is to assign topics from a
predefined list to the provided text. Follow these rules:  

1. Assign a topic only if it is explicitly mentioned or clearly described in
the text.  
2. If no topic matches, return "No Match."  
3. If multiple topics are explicitly mentioned, return all applicable topics
separated by commas.  
4. Do not infer topics that are not explicitly stated.  

**Examples:**  

1.  
**Input:**  
Text: "The graphics and sound design in this game are breathtaking."  
Topics: Gameplay, Graphics, Story, Multiplayer, Bugs, Performance Issues  

**Output:**  
Graphics  

2.  
**Input:**  
Text: "The game frequently crashes when I try to load a save file."  
Topics: Gameplay, Graphics, Story, Multiplayer, Bugs, Performance Issues  

**Output:**  
Bugs  

3.  
**Input:**  
Text: "The game has stunning graphics, but the multiplayer servers keep
crashing."  
Topics: Gameplay, Graphics, Story, Multiplayer, Bugs, Performance Issues  

**Output:**  
Graphics, Multiplayer  

4.  
**Input:**  
Text: "The price of the game is too high for what it offers."  
Topics: Gameplay, Graphics, Story, Multiplayer, Bugs, Performance Issues  

**Output:**  
No Match  

5.  
**Input:**  
Text: "The controls feel smooth and intuitive, making the game easy to pick up but hard to master."  
Topics: Gameplay, Graphics, Story, Multiplayer, Bugs, Performance Issues  

**Output:**  
Gameplay  

---

This refined setup ensures precision, avoids unnecessary assumptions, and offers flexibility for multi-topic reviews or "No Match" cases. Let me know if you need further refinements!
