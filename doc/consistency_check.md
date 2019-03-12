# 資料一致性檢查

1. 同一個synset內的sense需要彼此相連為synonymy
2. hypernym和hyponym是inverse relationships
3. troponym的inverse relationship是hypernym
4. 只有動詞sense才能有troponym
5. 只有名詞sense才能有hyponym
6. 每一個sense都必須要有相關連的synset
7. 每一個sense都必須要連結到lemma
8. synset或sense的連結關係不應該有cycle。為了計算簡便，是否僅檢查在k步內形成的cycle

