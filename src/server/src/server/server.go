package main

import (
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
)

// Handle each http request, perform routing
func handler(w http.ResponseWriter, r *http.Request) {
	defer fmt.Println()
	fmt.Println(r.RemoteAddr)
	fmt.Println(r.Method, r.URL)
	if r.Method == "POST" {
		if r.URL.Path == "/login" {
			authenticate(w, r)
		} else if r.URL.Path == "/registration" {
			create_account(w, r)
		} else if r.URL.Path == "/upload" {
			client_upload(w, r)
		} else if r.URL.Path == "/share" {
			client_share(w, r)
		}
	} else if r.Method == "GET" {
		if r.URL.Path == "/logout" {
			logout(w, r)
		} else if r.URL.Path == "/listshare" {
			client_share_list(w, r)
		} else if r.URL.Path == "/download" {
			client_download(w, r)
		}
	} else if r.Method == "DELETE" {
		client_delete(w, r)
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

func cleanup() {
	auth_save_db()
	share_save_db()
	fmt.Println("Bye")
}

func main() {
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt)
	signal.Notify(c, syscall.SIGTERM)
	go func() {
		<-c
		cleanup()
		os.Exit(0)
	}()

	os.MkdirAll("data", 0755)
	auth_load_db()
	share_load_db()
	auth_setup()
	share_setup()
	http.HandleFunc("/", handler)
	//http.ListenAndServeTLS(":8080","config/server.pem", "config/server.key", nil)
	http.ListenAndServe(":8080", nil)
}
