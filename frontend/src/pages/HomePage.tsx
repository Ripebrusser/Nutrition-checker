import { Link } from 'react-router-dom'

export function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-green-50 to-white">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-green-200/30 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-72 h-72 bg-green-200/20 rounded-full blur-3xl" />
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
          <div className="max-w-3xl">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-neutral-900 tracking-tight">
              Personalized Indian Nutrition <span className="text-green-600">Made Simple</span>
            </h1>
            <p className="mt-6 text-lg lg:text-xl text-neutral-600 max-w-2xl">
              Science-backed nutrition planning with authentic Indian recipes.
              Get personalized meal plans based on your health metrics, dietary preferences, and cultural preferences.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row gap-4">
              <Link
                to="/register"
                className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-green-600 hover:bg-green-700 transition-colors"
              >
                Get Started Free
              </Link>
              <Link
                to="/login"
                className="inline-flex items-center justify-center px-6 py-3 border border-neutral-300 text-neutral-700 rounded-lg text-base font-medium hover:bg-neutral-50 transition-colors"
              >
                Sign In
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-neutral-900 tracking-tight">
              Everything you need for personalized nutrition
            </h2>
            <p className="mt-4 text-lg text-neutral-600 max-w-2xl mx-auto">
              Science-backed nutrition planning with authentic Indian recipes
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard
              icon="🍽️"
              title="6,865+ Authentic Recipes"
              description="Curated Indian recipes from diverse regional cuisines with detailed ingredients and instructions."
            />
            <FeatureCard
              icon="🎯"
              title="Personalized Nutrition"
              description="ICMR 2020 guidelines with Mifflin-St Jeor BMR for science-backed nutrition targets."
            />
            <FeatureCard
              icon="🛡️"
              title="Dietary Safety"
              description="Hard constraints for allergies, Jain, vegan, vegetarian, and custom exclusions."
            />
            <FeatureCard
              icon="📅"
              title="Smart Meal Planning"
              description="Weekly meal plans with variety controls, prep time limits, and nutrition tracking."
            />
            <FeatureCard
              icon="🔬"
              title="Evidence-Based"
              description="ICMR 2020 RDA standards with IFCT 2017 food composition data."
            />
            <FeatureCard
              icon="🛡️"
              title="Safe by Design"
              description="Hard constraints never overridden. Missing nutrition clearly marked unavailable."
            />
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-20 bg-neutral-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-neutral-900 tracking-tight">
              How it works in 4 steps
            </h2>
            <p className="mt-4 text-lg text-neutral-600 max-w-2xl mx-auto">
              From profile to plate in minutes
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <StepCard
              step="01"
              title="Create Your Profile"
              description="Enter your health metrics, dietary preferences, allergies, and nutrition goals."
            />
            <StepCard
              step="02"
              title="Get Nutrition Targets"
              description="Get science-backed calorie, protein, carb, fat, and fiber targets based on ICMR 2020."
            />
            <StepCard
              step="03"
              title="Discover Recipes"
              description="Browse 6,865+ authentic Indian recipes filtered by your dietary needs."
            />
            <StepCard
              step="04"
              title="Build Meal Plans"
              description="Generate weekly meal plans with nutrition tracking and variety controls."
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-green-600">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
            Ready to start your nutrition journey?
          </h2>
          <p className="text-green-100 text-lg mb-8 max-w-2xl mx-auto">
            Join thousands getting personalized nutrition with authentic Indian recipes
          </p>
          <Link
            to="/register"
            className="inline-flex items-center justify-center px-8 py-4 border-2 border-white text-lg font-medium rounded-lg text-green-600 bg-white hover:bg-green-50 transition-colors"
          >
            Get Started Free
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-neutral-900 text-neutral-300 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <h3 className="text-white text-lg font-semibold mb-4">Indian Nutrition &amp; Diet Planner</h3>
              <p className="text-green-300 text-sm mb-4">
                Science-backed nutrition planning with authentic Indian recipes.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-4">Product</h4>
              <ul className="space-y-2 text-green-300 text-sm">
                <li><a href="/recipes" className="hover:text-green-300">Recipes</a></li>
                <li><a href="/recommendations" className="hover:text-green-300">Recommendations</a></li>
                <li><a href="/meal-planner" className="hover:text-green-300">Meal Planner</a></li>
                <li><a href="/nutrition-breakdown" className="hover:text-green-300">Nutrition Analysis</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-4">Resources</h4>
              <ul className="space-y-2 text-green-300 text-sm">
                <li><a href="/nutrition-targets" className="hover:text-green-300">Nutrition Targets</a></li>
                <li><a href="/meal-planner" className="hover:text-green-300">Meal Planner</a></li>
                <li><a href="/preferences" className="hover:text-green-300">Preferences</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-4">Legal</h4>
              <ul className="space-y-2 text-green-300 text-sm">
                <li><a href="#" className="hover:text-green-300">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-green-300">Terms of Service</a></li>
                <li><a href="#" className="hover:text-green-300">Data Policy</a></li>
              </ul>
            </div>
          </div>
          <div className="mt-12 border-t border-neutral-800 pt-8 text-center text-neutral-400 text-sm">
            <p>&copy; 2024 Indian Nutrition &amp; Diet Planner. All rights reserved.</p>
            <p className="mt-2 text-sm">
              Built with ICMR 2020 guidelines &amp; IFCT 2017 food composition data
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-neutral-200 hover:shadow-md transition-shadow">
      <div className="text-3xl mb-3">{icon}</div>
      <h3 className="text-lg font-semibold text-neutral-900 mb-2">{title}</h3>
      <p className="text-neutral-600">{description}</p>
    </div>
  )
}

function StepCard({ step, title, description }: { step: string; title: string; description: string }) {
  return (
    <div className="relative pl-12 pb-8 last:pb-0">
      <div className="absolute left-0 top-0 w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-green-700 font-bold text-sm">
        {step}
      </div>
      <div className="ml-12">
        <h3 className="text-lg font-semibold text-neutral-900 mb-2">{title}</h3>
        <p className="text-neutral-600">{description}</p>
      </div>
    </div>
  )
}

export default HomePage
