# 資料一致性檢查

## 檢查規則

### nodes
1. sense node必須有def和pos
2. synset node必須有gloss
3. 所有彼此為synonym的sense node，彼此必須有相同的def和pos，但sense node彼此之間不必然相同（因為可能src不一定相同）。


### edges
1. 同一個synset內的sense需要彼此相連為synonymy
2. hypernym和hyponym是inverse relationships
3. troponym的inverse relationship是hypernym
4. 只有動詞sense才能有troponym
5. 只有名詞sense才能有hyponym
6. 每一個sense都必須要連結到恰巧一個synset
7. 每一個sense都必須要連結到lemma
8. synset或sense的連結關係不應該有cycle。為了計算簡便，是否僅檢查在k步內形成的cycle

## 檢查後動作

### nodes
* nodes的錯誤（N1-N3）都跟資料本身有關，程式無法自動更正。只能把檢查未通過的nodes另外傳回一個invalid set。

### edges
* edges的規則（E1-E5）都是可自動更正的，Checker應該要能夠產生一個可修復這些錯誤的Annotator object。
* E6-E8無法自動修復，也只能傳回未通過的edges。
