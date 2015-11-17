package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
)

type test_struct struct {
	Test string
}

func handler(w http.ResponseWriter, r *http.Request) {
	body, _ := ioutil.ReadAll(r.Body)
	body2 := string(body)
	fmt.Println(body2)
	decoder := json.NewDecoder(r.Body)
	var t test_struct
	err := decoder.Decode(&t)
	if err == nil {
		fmt.Println("ERR")
	}
	fmt.Println(t)
	fmt.Fprintf(w, "Hi there, I love %s!", r.URL.Path[1:])
}

func main() {
	http.HandleFunc("/", handler)
	http.ListenAndServe(":8080", nil)
}
