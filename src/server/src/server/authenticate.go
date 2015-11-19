package main

import (
	"bytes"
	"encoding/hex"
	"encoding/gob"
	"encoding/json"
	"fmt"
	"os"
	//"io/ioutil"
	"crypto/rand"
	"golang.org/x/crypto/scrypt"
	"net/http"
)

type Response_authenticate struct {
	Status bool   `json:"status"`
	Token  string `json:"token"`
}

type Response_create_account struct {
	Status bool   `json:"status"`
}

// ===========================================
// Account and hashed password db
type record struct {
	Salt []byte
	Password []byte
}

var db map[string]record

// ===========================================
// Token db
type token struct {
	Token []string
}
// [token] = client_id
var token_db map[string]string



func setup() {
	db = make(map[string]record)
	token_db = make(map[string]string)
}

func _create_account_fail(w http.ResponseWriter, r *http.Request) {
	ret := &Response_create_account {
		Status: false}
	ret2, err := json.Marshal(ret)
	if err != nil {
		fmt.Println(err)
	}
	fmt.Fprintf(w, string(ret2))
	fmt.Println("Response: ", string(ret2))
}

func create_account(w http.ResponseWriter, r *http.Request) {
	// Parse POST form records
	r.ParseForm()
	client_id := r.FormValue("client_id")
	client_pw := r.FormValue("client_secret")
	fmt.Println("client_id", client_id)
	fmt.Println("client_pw", client_pw)

	// Check the client_id is not duplicated
	if _, ok := db[client_id]; ok {
		// Username already used, return false
		_create_account_fail(w, r)
		return
	}

	// Generate salt
	salt := make([]byte, 16)
	_, err := rand.Read(salt)
	if err != nil {
		fmt.Println("ERROR")
		_create_account_fail(w, r)
		return
	}

	// Compute hash(pw|salt)
	password, err:= scrypt.Key([]byte(client_pw), salt, 16384, 8, 1, 256)
	if err != nil {
		fmt.Println("ERROR")
		_create_account_fail(w, r)
		return
	}

	// Store the record into db
	db[client_id] = record {
		Salt: salt,
		Password: password,
	}

	// Return true to client
	ret := &Response_create_account {
		Status: true}
	ret2, err := json.Marshal(ret)
	if err != nil {
		fmt.Println(err)
	}
	fmt.Fprintf(w, string(ret2))
	fmt.Println("Response: ", string(ret2))
}

func save(filename string) {
	f, err := os.Create(filename)
	if err != nil {
		panic("cant open file")
	}
	defer f.Close()

	enc := gob.NewEncoder(f)
	if err := enc.Encode(db); err != nil {
		panic("cant encode")
	}
}

func load(filename string) {
	f, err := os.Open(filename)
	if err != nil {
		panic("cant open file")
	}
	defer f.Close()

	enc := gob.NewDecoder(f)
	if err := enc.Decode(&db); err != nil {
		panic("cant decode")
	}
}

// Verify the username and password are valid in database
func _authenticate(client_id string, client_pw string) bool {
	// Check the client_id is in the db
	fmt.Println(client_id)
	record, ok := db[client_id]
	if !ok {
		// Record not found
		fmt.Println("id not found")
		return false
	}

	// Compute hash(pw|salt)
	password, err:= scrypt.Key([]byte(client_pw), record.Salt, 16384, 8, 1, 256)
	if err != nil {
		fmt.Println("ERROR")
		return false
	}

	if bytes.Equal(password, record.Password) {
		return true
	} else {
		return false
	}
}

// Verify the token is valid and haven't expired
func verify_token(token string) (string, bool) {
	client_id, ok := token_db[token]
	if !ok {
		return client_id, false
	}
	return client_id, true
}

// Generate a token
func generate_token(client_id string) string {
	// Generate token
	token := make([]byte, 32)
	_, err := rand.Read(token)
	if err != nil {
		// Should not happen =(
		fmt.Println("Generate token ERROR")
		return ""
	}

	// convert token to hex string
	token_str := hex.EncodeToString(token)
	token_db[token_str] = client_id

	return token_str
}

func authenticate(w http.ResponseWriter, r *http.Request) {
	r.ParseForm()
	client_id := r.FormValue("client_id")
	client_pw := r.FormValue("client_secret")
	fmt.Println("client_id", client_id)
	fmt.Println("client_pw", client_pw)

	if _authenticate(client_id, client_pw) {
		// Generate token
		token := generate_token(client_id)

		// Response true and the token
		ret := &Response_authenticate{
			Status: true,
			Token:  token}
		ret2, err := json.Marshal(ret)
		if err != nil {
			fmt.Println(err)
		}
		fmt.Println("Response: ", string(ret2))
		fmt.Fprintf(w, string(ret2))
	} else {
		ret := &Response_authenticate{
			Status: false,
			Token:  ""}
		ret2, err := json.Marshal(ret)
		if err != nil {
			fmt.Println(err)
		}
		fmt.Println("Response: ", string(ret2))
		fmt.Fprintf(w, string(ret2))
	}
}
