import './AboutPage.css';

export default function AboutPage() {
  return (
    <div className="about-page">
      <div className="about-container">
        <h1>About ChainLines</h1>
        
        <section>
          <h2>What is ChainLines?</h2>
          <p>
            ChainLines is an open-source platform dedicated to documenting and visualizing 
            the evolutionary history of professional cycling teams from 1900 to the present day. We track team lineages, mergers, 
            splits, and transformations across more than a century of professional cycling history.
          </p>
          <p>
            Using an interactive D3.js "river" visualization, we show how teams evolve through rebrands, how squads merge together, 
            and how new teams emerge from existing organizations. Our system uses the <strong>Managerial Node</strong> concept to 
            represent the persistent legal entity behind a team—the organization that survives even when team names, sponsors, and 
            jerseys change.
          </p>
        </section>

        <section>
          <h2>Core Concepts</h2>
          <p>
            <strong>Managerial Node:</strong> The persistent legal entity that represents organizational 
            continuity across name changes and rebrandings.
          </p>
          <p>
            <strong>Team Era:</strong> A specific season snapshot of a team with complete metadata including name, UCI code, tier, 
            and sponsor information.
          </p>
          <p>
            <strong>Lineage Event:</strong> Structural changes that alter team identity—legal transfers, spiritual successions, 
            mergers, and splits that connect teams across time.
          </p>
          <p>
            <strong>Jersey Slice:</strong> Visual representation using sponsor color proportions to show team identity at a glance.
          </p>
        </section>

        <section>
          <h2>Our Mission</h2>
          <p>
            To create an accurate, comprehensive, and accessible record of professional cycling team histories, enabling fans, 
            researchers, historians, and enthusiasts to understand the complex web of team relationships and evolution over time. 
            We aim to preserve cycling's organizational heritage and make it freely available to everyone.
          </p>
        </section>

        <section>
          <h2>Technology Stack</h2>
          <p>
            ChainLines is built with modern web technologies: a <strong>Python FastAPI</strong> backend with <strong>PostgreSQL</strong> 
            database, and a <strong>React</strong> frontend using <strong>D3.js</strong> for interactive visualizations. The entire 
            application is containerized with Docker and includes automated testing, database migrations, and CI/CD workflows.
          </p>
          <p>
            We prioritize <strong>GDPR compliance</strong> by self-hosting fonts, using transparent authentication (Google OAuth), 
            and maintaining clear data handling practices in accordance with German data protection law (DSGVO).
          </p>
        </section>

        <section>
          <h2>Data Sources</h2>
          <p>
            Historical cycling data is collected through gentle web scraping from trusted sources including <strong>ProCyclingStats</strong>, 
            <strong>Wikipedia</strong>, and <strong>FirstCycling</strong>. We respect rate limits and robots.txt guidelines, and 
            supplement automated collection with community contributions and manual verification.
          </p>
        </section>

        <section>
          <h2>Community-Driven & Open Source</h2>
          <p>
            ChainLines is built by the cycling community, for the cycling community. This is a <strong>non-commercial, personal, 
            open-source project</strong> created for educational and historical documentation purposes. We believe in collaborative, 
            transparent knowledge sharing and welcome contributions from anyone passionate about cycling history.
          </p>
          <p>
            Our wiki-style editing system allows community members to propose changes, corrections, and additions. All edits are 
            reviewed through a moderation system to maintain data quality while encouraging broad participation.
          </p>
          <p>
            The entire codebase is licensed under the <strong>Apache License 2.0</strong> and is available on GitHub. Researchers, 
            developers, and fans are free to contribute, fork, and build upon our work. We're committed to maintaining transparency 
            and accessibility in all aspects of the project.
          </p>
        </section>

        <section>
          <h2>GitHub Repository</h2>
          <p>
            The complete source code, documentation, and project history are available on GitHub:
          </p>
          <p className="github-link">
            <a 
              href="https://github.com/fjungplan/chainlines" 
              target="_blank" 
              rel="noopener noreferrer"
              className="github-button"
            >
              <svg height="24" width="24" viewBox="0 0 16 16" fill="currentColor" style={{ marginRight: '8px' }}>
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
              </svg>
              Visit GitHub Repository: fjungplan/chainlines
            </a>
          </p>
          <p>
            <strong>Contributions welcome!</strong> Whether you want to report a bug, suggest a feature, fix a typo, or add 
            historical data, we encourage you to:
          </p>
          <ul>
            <li>Open an issue to report problems or suggest improvements</li>
            <li>Submit pull requests with code contributions</li>
            <li>Contribute historical data and corrections</li>
            <li>Help with documentation and translations</li>
            <li>Share the project with fellow cycling enthusiasts</li>
          </ul>
        </section>

        <section>
          <h2>Contact</h2>
          <p>
            For questions, licensing inquiries, or attribution clarifications, please open an issue on our 
            <a href="https://github.com/fjungplan/chainlines/issues" target="_blank" rel="noopener noreferrer"> GitHub repository</a>.
          </p>
          <p>
            <strong>Project Owner:</strong> fjungplan<br />
            <strong>License:</strong> Apache License 2.0<br />
            <strong>Year:</strong> 2025
          </p>
        </section>
      </div>
    </div>
  );
}
