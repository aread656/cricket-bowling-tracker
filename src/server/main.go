package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
)

func project_root() (string, error) {
	_, source, _, ok := runtime.Caller(0)
	if !ok {
		return "", fmt.Errorf("could not locate server source file")
	}
	return filepath.Dir(filepath.Dir(filepath.Dir(source))), nil
}

func get_video(w http.ResponseWriter, r *http.Request) {
	file, header, err := r.FormFile("video")
	w.Header().Set("Content-Type", "text/plain")
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		fmt.Fprintf(w, "Error: %v", err)
		return
	}
	header.Filename = filepath.Base(header.Filename)
	defer file.Close()
	fmt.Fprintf(w, "File: %s, Size: %d", header.Filename, header.Size)
	w.WriteHeader(http.StatusOK)
}

func save_video(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	src, header, err := r.FormFile("video")
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		fmt.Fprintf(w, "Error: %v", err)
		return
	}
	filename := filepath.Base(strings.ReplaceAll(header.Filename, "\\", "/"))
	session := strings.TrimSpace(r.FormValue("session"))
	if filename == "" || filename == "." || filename == ".." || session == "" || session == "." || session == ".." || strings.ContainsAny(session, `/\\`) {
		http.Error(w, "A filename and session date/folder are required", http.StatusBadRequest)
		return
	}
	defer src.Close()

	root, err := project_root()
	if err != nil {
		http.Error(w, "Could not locate project directory", http.StatusInternalServerError)
		return
	}
	uploadDir := filepath.Join(root, "src", "server", "uploads",session)
	if err := os.MkdirAll(uploadDir, 0755); err != nil {
		http.Error(w, "Could not prepare upload directory", http.StatusInternalServerError)
		return
	}
	path := filepath.Join(uploadDir, filename)
	dst, err := os.Create(path)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		fmt.Fprintf(w, "Error: %v", err)
		return
	}
	defer dst.Close()

	size, err := io.Copy(dst, src)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		fmt.Fprintf(w, "Error: %v", err)
		os.Remove(path)
		return
	}
	if size != header.Size {
		w.WriteHeader(http.StatusBadRequest)
		fmt.Fprint(w, "Error: uploaded file size did not match the declared size")
		os.Remove(path)
		return
	}
	w.WriteHeader(http.StatusOK)
	_ = json.NewEncoder(w).Encode(map[string]string{"filename": filename, "session": session})
}

func analyse_video(w http.ResponseWriter, r *http.Request){
	r.Body = http.MaxBytesReader(w,r.Body,1<<20)
	var request struct{
		Filename string `json:"filename"`
		Session string `json:"session"`
	}
	decoder := json.NewDecoder(r.Body)
	if err := decoder.Decode(&request); err != nil{
		http.Error(w,"Invalid JSON Request",http.StatusBadRequest)
		return
	}
	if _, err := decoder.Token(); err != io.EOF{
		http.Error(w,"JSON object must comtain at least one value",http.StatusBadRequest)
		return
	}
	if request.Filename == "" || request.Filename == "." || filepath.Base(request.Filename) != request.Filename || request.Session == "" || request.Session == "." || filepath.Base(request.Session) != request.Session {
		http.Error(w,"Filename must be a plain filename",http.StatusBadRequest)
		return
	}
	root,err := project_root()
	if err != nil{
		http.Error(w,"Couldn't locate root directory",http.StatusInternalServerError)
		return
	}
	upload_path := filepath.Join(root,"src","server","uploads",request.Session,request.Filename)
	if info, err := os.Stat(upload_path); err != nil || !info.Mode().IsRegular(){
		http.Error(w,"Selected file has not been uploaded",http.StatusInternalServerError)
		return
	}
	processor_path := filepath.Join(root,"src","processor","processor.py")
	cmd := exec.Command("python",processor_path,upload_path)
	var stdErr bytes.Buffer
	cmd.Stderr = &stdErr
	output, err := cmd.Output()
	if err != nil{
		http.Error(w,fmt.Sprintf("Error occurred during processing: %v\n%v\n",err,stdErr.String()),http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type","application/json")
	w.WriteHeader(http.StatusOK)
	w.Write(output)
}

func enableCORS(w http.ResponseWriter, r *http.Request){
	w.Header().Set("Access-Control-Allow-Origin","http://localhost:5173")
	w.Header().Set("Access-Control-Allow-Methods","GET,POST,OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers","Content-Type")
	if r.Method=="OPTIONS"{
		w.WriteHeader(http.StatusOK)
		return
	}
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /api/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("Server is running"))
	})
	mux.HandleFunc("POST /api/videos", get_video)
	mux.HandleFunc("POST /api/save", save_video)
	mux.HandleFunc("POST /api/analyse", analyse_video)
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		enableCORS(w, r)
		if r.Method == "OPTIONS" {return}
		mux.ServeHTTP(w, r)
	})
	log.Fatal(http.ListenAndServe(":8080", handler))
}
