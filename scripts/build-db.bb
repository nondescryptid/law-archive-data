#!/usr/bin/env bb

(require '[babashka.process :refer [shell sh process]]
         '[babashka.fs :as fs]
         '[cheshire.core :as json]
         '[clojure.string :as str]
         '[taoensso.timbre :as timbre])

(def MERGESTAT_BINARY "mergestat")
(def DB_FILE "data/data.db")

(defn download-mergestat []
  (timbre/info "Downloading mergestat")
  (sh "wget" "https://github.com/mergestat/mergestat-lite/releases/download/v0.6.1/mergestat-linux-amd64.tar.gz")
  (timbre/info "Extracting mergestat")
  (sh "tar -xvf" "mergestat-linux-amd64.tar.gz")
  (timbre/info "Cleaning up unnecessary mergestat files")
  (sh "rm" "mergestat-linux-amd64.tar.gz" "libmergestat.so")
  (timbre/info "Setting permissions for mergestat")
  (sh "chmod +x" MERGESTAT_BINARY))

(defn get-ignored-commits [file]
  (when (not (fs/exists? MERGESTAT_BINARY))
    (download-mergestat))
  (->> (-> (sh "./mergestat -f json"
               "SELECT files.path, hash FROM commits, files WHERE files.path IS NOT '" file "'")
           :out
           (json/parse-string true))
       (map :hash)
       (str/join " ")))

(defn generate-db
  ([namespace input-file]
   (generate-db namespace input-file nil))
  ([namespace input-file skip]
   (-> (str "poetry run git-history file"
            " " DB_FILE
            " " input-file
            " --namespace " namespace
            (if (nil? skip) "" (str " --skip " (str "'" skip "'"))))
       (shell))))

(defn- run-sql-on-db [f]
  (let [stream (-> (process ["cat" f]) :out)]
    @(process ["sqlite3" DB_FILE] {:in stream
                                   :out :inherit})))

(def HEARINGS_JSON "data/hearings.json")
(def SC_JSON "data/sc.json")
(def PDPC_UNDERTAKINGS_JSON "data/pdpc-undertakings.json")

(defn run []
  (generate-db "hearings" HEARINGS_JSON
               (get-ignored-commits HEARINGS_JSON))
  (generate-db "sc" SC_JSON
               (get-ignored-commits SC_JSON))
  (generate-db "pdpc-undertakings" PDPC_UNDERTAKINGS_JSON
               (get-ignored-commits PDPC_UNDERTAKINGS_JSON)))

(run)