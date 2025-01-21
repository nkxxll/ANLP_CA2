<!-- spell-checker:disable -->

# Notes

- we can start writing the documentation right now much less work later

## Methodik

- topics muessen wissenschaftlich ausgewaehlt werden
  - nachschauen nach bestimmten game topics
  - discutieren
  - und dann im paper darstellen wie sie ausgesucht wurden
- wie machen wir bin classification und warum haben wir die methode gewaehlt ist sie besser oder
  schlechter als die bin classification von ca1
- llm classification for training data
  - wir haben ein zu niedrige menge an trainingsdaten
  - wir wollen die daten aufbereiten und ein llm benutzen um uns dabei zu helfen
  - wir werden die classification-daten des llm mit von hand klassifizierten daten evaluieren
  - welches llm ist am besten geeignet und warum wie lange braucht es welche Resourcen werden
    verwendet
- Multi-label-classification
  - wir werden ein specifisches neuronales netz verwenden, um reviews mit topics zu klassifizierten
  - Multi-label-classification
  - dieses nn braucht natuerlich viel weniger zeit zum klassifizierten und ist resourcen sparender
  - es ist auch auf game reviews und nicht auf allen texten der welt trainiert
  - wie performt es auf den trainingsdaten die wir mit dem llm generiert haben
  - wie performt es gegen unsere trainingsdaten

## Problem

- bin classification of reviews
  - sentiment analysis
  - better or worse than the ca1 classification
- llm for training data generation
  - which llm is why better how do we test it
  - how much ressources
  - how much better is a tailored solution from us
- tailored nn Multi-label-classification
  - how good does it perform on the generated training data
  - how good does it perform on our training data

## Solution

1. Binary Classification with ?RNN?, besser schlechter als ca1 classification
2. LLM training data generation
3. Multi-label-classification von reviews zu topics die wir ausgewaehlt haben
