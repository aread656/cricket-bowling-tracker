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
)

func projectRoot() (string, error) {
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
	w.Header().Set("Content-Type", "text/plain")
	src, header, err := r.FormFile("video")
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		fmt.Fprintf(w, "Error: %v", err)
		return
	}
	header.Filename = filepath.Base(header.Filename)
	defer src.Close()

	root, err := projectRoot()
	if err != nil {
		http.Error(w, "Could not locate project directory", http.StatusInternalServerError)
		return
	}
	uploadDir := filepath.Join(root, "src", "server", "uploads")
	if err := os.MkdirAll(uploadDir, 0755); err != nil {
		http.Error(w, "Could not prepare upload directory", http.StatusInternalServerError)
		return
	}
	path := filepath.Join(uploadDir, header.Filename)
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
	fmt.Fprintf(w, "File %v has been saved", header.Filename)
}

func analyse_video(w http.ResponseWriter, r *http.Request) {
	r.Body = http.MaxBytesReader(w, r.Body, 1<<20)
	var request struct {
		Filename string `json:"filename"`
	}
	decoder := json.NewDecoder(r.Body)
	if err := decoder.Decode(&request); err != nil {
		http.Error(w, "Invalid JSON request", http.StatusBadRequest)
		return
	}
	if _, err := decoder.Token(); err != io.EOF {
		http.Error(w, "Request must contain one JSON value", http.StatusBadRequest)
		return
	}
	if request.Filename == "" || filepath.Base(request.Filename) != request.Filename || request.Filename == "." {
		http.Error(w, "filename must be a plain uploaded filename", http.StatusBadRequest)
		return
	}

	root, err := projectRoot()
	if err != nil {
		http.Error(w, "Could not locate project directory", http.StatusInternalServerError)
		return
	}
	uploadPath := filepath.Join(root, "src", "server", "uploads", request.Filename)
	if info, err := os.Stat(uploadPath); err != nil || !info.Mode().IsRegular() {
		http.Error(w, "Uploaded video not found", http.StatusNotFound)
		return
	}
	processorPath := filepath.Join(root, "src", "processor", "processor.py")
	cmd := exec.Command("python", processorPath, uploadPath)

	var stderr bytes.Buffer
	cmd.Stderr = &stderr

	output, err := cmd.Output()
	if err != nil {
		http.Error(w, fmt.Sprintf("Processing failed: %v\n%s", err, stderr.String()), http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write(output)
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /api/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("Server is running"))
	})
	mux.HandleFunc("POST /api/videos", get_video)
	mux.HandleFunc("POST /api/save", save_video)
	mux.HandleFunc("POST /api/analyse", analyse_video)
	log.Fatal(http.ListenAndServe(":8081", mux))
}
