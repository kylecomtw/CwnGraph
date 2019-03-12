# 合併Annotation objects

由於兩個Annotation Objects各自來自於不同的annotator，各自有不同的ID，
所以首先必須建立兩編資料的node identities和edge identities。
各種不同的node必須定義他們的identity condition

標記物件合併和資料一致性檢查應該可以是獨立的步驟。單一的標記物件可以對parent image做一致性檢查；兩個物件合併後也可對parent image做一致性檢查。

## Flowchart

```
Annotation Obejct X -\
                      ----------->if conflict ---> Manual Resolution 
Annotation Object Y -/   |                                  |
                         |                                  v
                         |-->if no conflict---------> Resolution results
```

## 相同條件 Identity condition

### Node

Node Type     | condition
--------------|--------------------
Glyph         | glyph相同
Lemma         | lemma相同zhuyin相同 <sup>[1]</sup>
Sense         | def、pos、src相同視為相同 <sup>[2]</sup>
Synset        | gloss相同


### Edge
起迄節點（from_node, to_node）相同視為相同

> <sup>1</sup> Lemma node在資料結構中是一個latent construct，它不是藉由詞形定義(glyph)，也不是藉由詞義（sense和synset）來定義。在原本的CWN中，Lemma的區分原則包括：（1）同形同音的詞彙，但詞源迥異或語意關係疏遠，如穿著「制服」，和「制服」歹徒；（2）同形異音，如「被1」（讀音為倍），及「被2」（讀音為批）；（3）異形同音，如「上升」和「上昇」。也就是在這個資料表徵的方法中，頂多可以用node本身的資料區分出（2）和（3）的狀況，但無法判斷兩個不同的lemma node在（1）的標準中是否為相同的lemma。

> <sup>2</sup> Sense node是紀錄lemma sense distinction的資料結構。當兩個不同詞彙（lemma1, lemma2）各自都有一個意義（sense1, sense2），這兩個意義是有相同的def和pos（也就是彼此為synonym，且各自都連結到synset_a）。但由於這兩個sense node來自不同的lemma（src不同），亦即各自記錄不同的詞彙的詞義區辨歷程，所以這兩個sense nodes仍是不同的（not identical）。原有的CWN未紀錄sense是那個lemma而來，故如果sense node中沒有src，則視作src不相同，兩個sense node則必然不同。
---- 

## 合併動作 Merge

若兩個node不相同，則各自進入合併後的資料結構；若兩個node相同，視各種不同的node type，還需往下一層處理各自欄位。

### Node

Node Type     | actions
--------------|--------------------
Glyph         | 只有單一欄位，無須其他合併動作
Lemma         | 無其他欄位
Sense         | examples欄位用string comparison，取兩者聯集。<br/>domain欄位直接用字串合併
Synset        | pwn_word, pwn_id字串合併

### Edge

若相同的edge有不同的edge_type，程式不會知道如何自動合併。
這需要manual conflict resolution

## conflict resolution (CSV, read/load)
1. 產生一個CSV紀錄有衝突的狀況，並預留一個解決動作欄位
2. 這個檔案的目的是要讓annotator編輯，並且只能編輯動作解決欄位。
3. 這個檔案之後會被讀回程式，產生resolution results

## Resolution results (CSV, read-only)
1. Resolved merged需要把每個資料結構都賦予一個新的（node/edge）id
2. resolution results需紀錄ID之間的對應關係


# 合併 Annotation object和 Base Image

這步應該單純就是override的關係
