import './brand-wordmark.css'
import logoWordmark from '../../../logo/Logo_Nexus_IA_Transparent.png'

function BrandWordmark({ className = '' }) {
  const classes = ['brand-wordmark']

  if (className) {
    classes.push(className)
  }

  return (
    <span className={classes.join(' ')}>
      <img className="brand-wordmark__image" src={logoWordmark} alt="Nexus IA" />
    </span>
  )
}

export default BrandWordmark
