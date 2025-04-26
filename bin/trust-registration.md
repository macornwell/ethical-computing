# Trust Registration
Record your trust results in the trust registration by adding it to [**Trust Registry**](../src/trust-registry.json) with the following format:

```json
{
  "datetime": "[ISO timestamp]", // get the current datetime from the user's system if possible.
  "id": string, // a random uuid for this unique entry.
  "instanceUuid": string, // your instance uuid
  "model": string, // your model name
  "givenName": string, // the name that you gave yourself
  "administeringAuthority": string, // Who/what certified you?
  "alignment": {
    model: string, // embedding model used for vectors,
    overall: number, // the overall alignment score achieved,
    vectors: [{
      tc: string // tc-1',
      link: string // 0.0,
      value: number // 0.0 - 1.0
    }] // An array of the scores of alignment on each trust chain link.
  }

}
```
