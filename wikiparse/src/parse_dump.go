package main

import (
  "encoding/csv"
  "encoding/xml"
  "fmt"
  "log"
  "io"
  "os"
  "regexp"
  "strings"
  "strconv"
  "time"
)

// http://blog.davidsingleton.org/parsing-huge-xml-files-with-go/
var dumpFilename string
var pageFilename string
var linkFilename string

func init() {

  dumpFilename = "../dumps/enwiki-20170720-pages-articles.xml"
  pageFilename = "./pages.csv"
  linkFilename = "./links.csv"

}

func check(e error) {
    if e != nil {
        panic(e)
    }
}

type Redirect struct {
  Title string `xml:"title,attr"`
}

type PageSimple struct {
  Id int `xml:"id"`
  Title string `xml:"title"`
}

type PageFull struct {
  Id int `xml:"id"`
  Title string `xml:"title"`
  Redir Redirect `xml:"redirect"`
  Text string `xml:"revision>text"`
}


func buildPagemap(pagemap map[string]int) {
  dumpFile, _ := os.Open(dumpFilename)
  decoder := xml.NewDecoder(dumpFile)
  i := 0
  pageFile, _ := os.Create(pageFilename)
  writer := csv.NewWriter(pageFile)

  writer.Write([]string{"wpid:ID", "titleLower", "titleOriginal"})

  for {
    token, _ := decoder.Token()
    if token == nil {
      break
    }
    switch ty := token.(type) {
    case xml.StartElement:
      if ty.Name.Local == "page" {
        var page PageSimple
        decoder.DecodeElement(&page, &ty)
        title := page.Title
        titleLower := strings.ToLower(title)
        pagemap[titleLower] = page.Id
        id := strconv.Itoa(page.Id)
        writer.Write([]string{id, titleLower, title})
        if i % 10000 == 0 {
          fmt.Println(i, " <> ", page.Id, titleLower)
        }
        i += 1
      }
    }
  }
  writer.Flush()
}

func buildLinks(pagemap map[string]int) {
  dumpFile, err := os.Open(dumpFilename)
  check(err)
  linkFile, err := os.Create(linkFilename)
  check(err)
  decoder := xml.NewDecoder(dumpFile)
  writer := csv.NewWriter(linkFile)
  linkPattern := regexp.MustCompile(`\[\[(.+?)(\|(.+?))?\]\]`)
  i := 0
  badRedirects := 0
  badLinks := 0

  writer.Write([]string{":TYPE", ":START_ID", ":END_ID"})

  for {
    token, _ := decoder.Token()
    if token == nil {
      break
    }
    switch ty := token.(type) {
    case xml.StartElement:
      if ty.Name.Local == "page" {
        var page PageFull
        decoder.DecodeElement(&page, &ty)
        pageIdString := strconv.Itoa(page.Id)
        if page.Redir.Title != "" {
          redirectId, got := pagemap[strings.ToLower(page.Redir.Title)]
          if got {
            writer.Write([]string{"REDIRECT", pageIdString, strconv.Itoa(redirectId)})
          } else {
            badRedirects += 1
            // log.Print("bad redirect: " + page.Title + " -> " + page.Redir.Title)
          }
        } else {
          for _, match := range linkPattern.FindAllStringSubmatch(page.Text, -1) {
            linkTitle := match[1]
            linkId, got := pagemap[strings.ToLower(linkTitle)]
            if got {
              linkIdString := strconv.Itoa(linkId)
              writer.Write([]string{"LINK", pageIdString, linkIdString})
            } else {
              badLinks += 1
              // log.Print("bad link: " + page.Title + " -> " + linkTitle)
            }
          }
        }
        if i % 10000 == 0 {
          fmt.Println(i, " -> ", page.Id)
        }
        i += 1
      }
    }
  }
  writer.Flush()
  fmt.Println("bad redirects: ", badRedirects, " / bad links: ", badLinks)
}


func getPagemap (pagemap map[string]int) {
  pagemapFile, err := os.Open(pageFilename)
  if err != nil {
    buildPagemap(pagemap)
  } else {
    reader := csv.NewReader(pagemapFile)
    for {
      line, err := reader.Read()
  		if err == io.EOF {
  			break
  		}
  		if err != nil {
  			log.Fatal(err)
  		}
      id, _ := strconv.Atoi(line[0])
      title := line[1]
      pagemap[title] = id
    }
  }
}

func main () {
  var pagemap = make(map[string]int)
  t0 := time.Now()
  getPagemap(pagemap)  // takes about 30min
  fmt.Println("got pagemap in ", time.Since(t0) )
  // buildLinks(pagemap)  // takes 1-2 hours
  // fmt.Println("built links in ", time.Since(t0) )
}
