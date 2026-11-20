import {useState} from "react"
import "./App.css"
import UploadForm from "./UploadForm"
import AnalyseVideo from "./analyse"

function App(){
  const [file,setFile] = useState<File|null>(null)
  const [upload,setUpload] = useState<{filename:string;session:string}|null>(null)
  return (
    <main className="app-shell">
      <header className="topbar">
        <span className="brand-mark" aria-hidden="true">✦</span>
        <span>Cricket Bowling Tracker</span>
      </header>

      <section className="hero" aria-labelledby="page-title">
        <p className="eyebrow">Bowling analysis</p>
        <h1 id="page-title">Make every delivery count.</h1>
        <p className="hero-copy">Upload a bowling video and get started with your delivery analysis.</p>
      </section>

      <section className="workflow" aria-label="Video analysis">
        <div className="workflow-heading">
          <span className="step-number" aria-hidden="true">01</span>
          <div>
            <h2>Start with a video</h2>
            <p>Choose a clip from your device to begin.</p>
          </div>
        </div>
        <UploadForm file={file} setFile={setFile} onSaved={setUpload}/>
        <div className="workflow-footer">
          <p className="helper-text">A clear side-on or front-on view works best.</p>
          <AnalyseVideo file={file} upload={upload}/>
        </div>
      </section>

      <p className="page-note">Your session is ready when you are.</p>
    </main>
  )
}
export default App
