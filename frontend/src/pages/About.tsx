import AlumniGallery from '../components/AlumniGallery'
import SidePhoto from '../components/SidePhoto'
import type { HeroStyle } from '../heroStyle'

export default function About() {
  return (
    <>
      <section className="hero hero--short" style={{ '--hero-photo': "url('/campus/sterling-library.jpg')" } as HeroStyle}>
        <div className="hero__watermark">Campus Customs</div>
        <div className="hero__inner">
          <h1>About Campus Customs</h1>
          <p className="hero__lede">Merch made by people who actually live here.</p>
        </div>
      </section>

      <section className="section">
        <SidePhoto src="/campus/old-campus.jpg" alt="Old Campus courtyard, Yale University">
          <h2>Our story</h2>
          <p>
            Campus Customs started with a simple observation: the best sweatshirt on campus is the
            one that says exactly where you belong. Your residential college, your team, your
            school, your family weekend. So we set out to make merch that fits those details.
          </p>
        </SidePhoto>

        <SidePhoto src="/campus/beinecke-library.jpg" alt="Beinecke Rare Book & Manuscript Library, Yale University" align="right">
          <h2>What we make</h2>
          <p>
            Hoodies for library all-nighters, crewnecks for the walk to class, tees for game day,
            and quarter-zips for when you want to look put together without trying too hard. Every
            piece is printed in small runs and comes in sizes XS through XXL.
          </p>
        </SidePhoto>

        <h2>Ask us anything</h2>
        <p className="prose">
          Not sure which color or size to pick? Use the chat in the corner. It knows our catalogue
          and can tell you what things cost and what's still in stock.
        </p>
      </section>

      <section className="section section--band reveal">
        <h2>Yale faces we like to remember</h2>
        <p>A few alumni whose names outlasted their graduating class.</p>
        <AlumniGallery />
      </section>
    </>
  )
}
