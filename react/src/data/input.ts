import { StoreType } from "./data";
import { DataHandle } from "./handle";
import { Schema } from "./schema";

export class InputHelper {
    constructor(private schema: Schema) {
        
    }

    getInputProps = <D, I, M, F>(dataHandle: DataHandle<M, F>, storeType: StoreType<M, F>) => {
        
    }
}
