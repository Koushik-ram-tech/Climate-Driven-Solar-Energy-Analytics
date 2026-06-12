import { useBackend } from './hooks/useBackend'
import { Navbar }            from './components/ui/Navbar'
import { HeroSection }       from './components/sections/HeroSection'
import { PredictionSection } from './components/sections/PredictionSection'
import { PerformanceSection }from './components/sections/PerformanceSection'
import { XAISection }        from './components/sections/XAISection'
import { VIFSection }        from './components/sections/VIFSection'
import { PipelineSection }   from './components/sections/PipelineSection'
import { ResearchSection }   from './components/sections/ResearchSection'
import { FooterSection }     from './components/sections/FooterSection'

export default function App() {
  const {
    health, healthLoading,
    cities,
    selectedCity, setSelectedCity,
    selectedDate, setSelectedDate,
    prediction, predError, predLoading, runPredict,
    explain, explainLoading, explainError,
  } = useBackend()

  const apiOnline = !healthLoading && !!health && health.status === 'ok'

  return (
    <div className="min-h-screen">
      <Navbar apiOnline={apiOnline} />

      <main>
        <HeroSection health={health} />
        <PredictionSection
          cities={cities}
          selectedCity={selectedCity}
          setSelectedCity={setSelectedCity}
          selectedDate={selectedDate}
          setSelectedDate={setSelectedDate}
          prediction={prediction}
          predLoading={predLoading}
          predError={predError}
          onPredict={runPredict}
        />
        <PerformanceSection />
        <XAISection
          explain={explain}
          explainLoading={explainLoading}
          explainError={explainError}
        />
        <VIFSection />
        <PipelineSection />
        <ResearchSection />
      </main>

      <FooterSection />
    </div>
  )
}
