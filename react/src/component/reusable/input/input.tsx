export type SrInputBaseProps<T> = {
    value: T,
    onChange: (newValue: T) => void,
    isInvalid: boolean
}
