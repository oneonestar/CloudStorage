package main

import (
	//"encoding/json"
	"fmt"
	//"io/ioutil"
	"net/http"
)

func handler(w http.ResponseWriter, r *http.Request) {
	/*err := r.ParseMultipartForm(32 << 20)
	if err != nil {
		fmt.Println(err)
	}*/
	defer fmt.Println()
	fmt.Println(r.RemoteAddr)
	fmt.Println(r.Method)
	fmt.Println(r.URL)
	if r.Method == "POST" {
		if r.URL.Path == "/login" {
			authenticate(w, r)
		} else if r.URL.Path == "/registration" {
			create_account(w, r)
		} else if r.URL.Path == "/upload" {
			client_upload(w, r)
		}
	} else if r.Method == "GET" {
		client_download(w, r)
	}
	/*
		fmt.Println(r.FormValue("myinfo"))
		fmt.Println(r.FormValue("document"))
		fmt.Println(r.Form)
		fmt.Println("scheme", r.URL)
		fmt.Println("scheme", r.URL.Path)
		fmt.Println(r.Form["url_long"])
		fmt.Println("scheme", r.URL.Scheme)
		//str := r.FormValue("myinfo2")
		str := r.FormValue("files")
		fmt.Println(str)*/
}

func main() {
	setup()
	http.HandleFunc("/", handler)
	//http.ListenAndServeTLS(":8080","config/server.pem", "config/server.key", nil)
	http.ListenAndServe(":8080", nil)
}
