package main

import (
	//"encoding/json"
	"fmt"
	"io"
	"os"
	//"io/ioutil"
	"net/http"
)

type test_struct struct {
	Test string
}

func client_upload(w http.ResponseWriter, r *http.Request) {
	file, handler, err := r.FormFile("document")
	if err != nil {
		fmt.Println(err)
		return
	}
	defer file.Close()
	fmt.Fprintf(w, "%v", handler.Header)
	f, err := os.OpenFile("data/"+r.URL.Path, os.O_WRONLY|os.O_CREATE, 0666)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer f.Close()
	io.Copy(f, file)
	//fmt.Fprintf(w, "Hi there, I love %s!", r.URL.Path[1:])
	fmt.Fprintf(w, "Success")
}

func client_download(w http.ResponseWriter, r *http.Request) {
	filename := r.URL.Path
	http.ServeFile(w, r, "data/"+filename)
}

func handler(w http.ResponseWriter, r *http.Request) {
	r.ParseMultipartForm(32 << 20)
	fmt.Println(r.Method)
	fmt.Println(r.URL)
	if r.Method == "POST" {
		client_upload(w, r)
	} else if r.Method == "GET" {
		client_download(w, r)
	}
	//fmt.Println(r)
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
	http.HandleFunc("/", handler)
	http.ListenAndServeTLS(":8080","config/server.pem", "config/server.key", nil)
}
