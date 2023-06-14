export function mapProperties<I, O>(obj: {[key: string]: I}, mapFunc: (name: string, value: I) => O): {[key: string]: O} {
    return Object.fromEntries(
        Object.entries(obj).map(([propName, propValue]) => {
            return [propName, mapFunc(propName, propValue)]
        })
    )
}

/**
 * https://stackoverflow.com/questions/51804810/how-to-remove-fields-from-a-typescript-interface-via-extension \
 * Equals the type with certain fields omitted \
 * Ex: `Omit<HTMLTextElement, 'value'|'text-align'>`
 */
export type Omit<T, K extends keyof T> = Pick<T, Exclude<keyof T, K>>

export type KeyValuePair<K, V> = {
    key: K,
    value: V
}

export class Dictionary<K, V> {
    constructor(initialRecords?: KeyValuePair<K, V>[]) {
        this.records = [...(initialRecords || [])];
    }

    private comparator = (searchKey: K) => (element: KeyValuePair<K, V>) => element.key === searchKey
    private records: KeyValuePair<K, V>[] = [];

    get = (key: K): V => {
        return this.records.find(this.comparator(key))?.value;
    }

    contains = (key: K): boolean => {
        return this.records.find(this.comparator(key)) !== undefined;
    }

    items = (): KeyValuePair<K, V>[] => {
        return [...this.records];
    }

    remove = (key: K): V => {
        let idx = this.records.findIndex(this.comparator(key));
        if(idx >= 0) {
            return this.records.splice(idx, 1)[0].value;
        }
        return undefined;
    } 

    put = (key: K, value: V): void => {
        let idx = this.records.findIndex(this.comparator(key));
        if(idx >= 0) {
            this.records.splice(idx, 1);
        }
        this.records.push({
            key,
            value
        })
    }

    clear = (): void => {
        this.records = [];
    }
}
