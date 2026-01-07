export interface Message {
  id: string
  author: string
  text: string
  timestamp: string
  self?: boolean
}
