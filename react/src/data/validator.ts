/**
 * Returns true if valid, false otherwise
 */
export type SrValidator<T> = (value: T) => boolean

const INT_REGEXP = /^[-+]?\d+$/;
const FLOAT_REGEXP = /^\s*(\-|\+)?(\d+|(\d*(\.\d*)))([eE][+-]?\d+)?\s*$/;


export const IntegerValidator: SrValidator<string> = (val: string) => {
    return INT_REGEXP.test(val);
}

export const FloatValidator: SrValidator<string> = (val: string) => {
    return FLOAT_REGEXP.test(val);
}

export const RequiredValidator: SrValidator<any> = (val: any) => {
    return !(val === undefined || val === null);
}

export class Validators<T> {
    constructor(private validators: SrValidator<T>[]) {
        
    }

    validate = (value: T) => {
        return this.validators.reduce((prev, vd) => prev && vd(value), true);
    }
}
