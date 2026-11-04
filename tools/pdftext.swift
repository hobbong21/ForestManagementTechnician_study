import Foundation
import PDFKit
// usage: pdftext in.pdf out.txt  — pages separated by \f
let a = CommandLine.arguments
guard let doc = PDFDocument(url: URL(fileURLWithPath: a[1])) else { print("FAIL"); exit(1) }
var out = ""
for i in 0..<doc.pageCount { out += (doc.page(at: i)?.string ?? "") + "\n\u{0C}\n" }
try! out.write(toFile: a[2], atomically: true, encoding: .utf8)
print(doc.pageCount)
