package main

import (
	"encoding/json"
	"log"
	"net/http"
)

type test_struct struct {
	Test string
}

func test(rw http.ResponseWriter, req *http.Request) {
	req.ParseForm()
	log.Println(req.Form)
	//LOG: map[{"test": "that"}:[]]
	var t test_struct
	for key, _ := range req.Form {
		log.Println(key)
		//LOG: {"test": "that"}
		err := json.Unmarshal([]byte(key), &t)
		if err != nil {
			log.Println(err.Error())
		}
	}
	log.Println(t.Test)
	//LOG: that
}

func main() {
	http.HandleFunc("/", test)
	log.Fatal(http.ListenAndServe(":8080", nil))
}
