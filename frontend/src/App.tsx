import {useState} from "react"
import UploadForm from "./UploadForm"
import AnalyseVideo from "./analyse"

function App(){
  const [file,setFile] = useState<File|null>(null)
  return (
    <div>
      <h1>Cricket Bowling Tracker</h1>
      <UploadForm file={file} setFile={setFile}/>
      <AnalyseVideo file={file}/>
    </div>
  )
}
export default App