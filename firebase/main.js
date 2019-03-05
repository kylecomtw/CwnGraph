var admin = require("firebase-admin");
var serviceAccount = require("./service_account_key.json");

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: "https://annie-frenny.firebaseio.com"
});
let db = admin.firestore();

function upload_data(db){
    let nodes = require('../cwn_graph_nodes.json');
    let edges = require('../cwn_graph_edges.json');
    console.log(`|V|: ${Object.keys(nodes).length},`,
                `|E|: ${Object.keys(edges).length}`);

    let counter = 0;
    let batch = db.batch();
    
    let nV = Object.keys(nodes).length;
    let cwn_ref = db.collection("cwn");
    for(const [node_id, node_data] of Object.entries(nodes)){            
        counter += 1;        
        let cwn_doc = cwn_ref.doc(node_id);
        batch.set(cwn_doc, {data: node_data});
        if (counter > 1000) break;
        if (counter % 200 == 0) {
            let _counter = counter;            
            batch.commit().then((x)=>{
                console.log(`${_counter} / ${nV}`);
            });
            batch = db.batch();
        }
    }
}

upload_data(db);

