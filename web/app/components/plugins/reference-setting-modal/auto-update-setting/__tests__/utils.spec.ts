<<<<<<< HEAD:web/app/components/plugins/reference-setting-modal/auto-update-setting/utils.spec.ts
import { convertLocalSecondsToUTCDaySeconds, convertUTCDaySecondsToLocalSeconds } from './utils'

describe('convertLocalSecondsToUTCDaySeconds', () => {
  it('should convert local seconds to UTC day seconds correctly', () => {
    const localTimezone = 'Asia/Shanghai'
    const utcSeconds = convertLocalSecondsToUTCDaySeconds(0, localTimezone)
    expect(utcSeconds).toBe((24 - 8) * 3600)
  })

  it('should convert local seconds to UTC day seconds for a specific time', () => {
    const localTimezone = 'Asia/Shanghai'
    expect(convertUTCDaySecondsToLocalSeconds(convertLocalSecondsToUTCDaySeconds(0, localTimezone), localTimezone)).toBe(0)
  })
})
=======
import { convertLocalSecondsToUTCDaySeconds, convertUTCDaySecondsToLocalSeconds } from '../utils'

describe('convertLocalSecondsToUTCDaySeconds', () => {
  it('should convert local seconds to UTC day seconds correctly', () => {
    const localTimezone = 'Asia/Shanghai'
    const utcSeconds = convertLocalSecondsToUTCDaySeconds(0, localTimezone)
    expect(utcSeconds).toBe((24 - 8) * 3600)
  })

  it('should convert local seconds to UTC day seconds for a specific time', () => {
    const localTimezone = 'Asia/Shanghai'
    expect(convertUTCDaySecondsToLocalSeconds(convertLocalSecondsToUTCDaySeconds(0, localTimezone), localTimezone)).toBe(0)
  })
})
>>>>>>> upstream/main:web/app/components/plugins/reference-setting-modal/auto-update-setting/__tests__/utils.spec.ts
