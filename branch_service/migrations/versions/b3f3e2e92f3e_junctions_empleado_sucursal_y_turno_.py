"""junctions empleado_sucursal y turno_empleado, eliminar empleado.fkSucursal

Revision ID: b3f3e2e92f3e
Revises: 17d479a46af6
Create Date: 2026-06-06 11:10:15.208632

Notas:
 - Las tablas empleado_sucursal y turno_empleado ya existen en la BD (creadas vía db.create_all);
   esta migración no las recrea. Solo registra el cambio de modelo y migra los datos antiguos
   de empleado.fkSucursal hacia la junction antes de eliminar la columna.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b3f3e2e92f3e'
down_revision = '17d479a46af6'
branch_labels = None
depends_on = None


def upgrade():
    # Backfill: copiar empleado.fkSucursal a la junction empleado_sucursal antes de eliminar la columna.
    op.execute(
        """
        INSERT INTO empleado_sucursal (oid, fkEmpleado, fkSucursal, createdAt, updatedAt, estatus)
        SELECT UUID(), e.oid, e.fkSucursal, NOW(), NOW(), 'ACTIVO'
        FROM empleado e
        WHERE e.fkSucursal IS NOT NULL
          AND e.estatus != 'ELIMINADO'
          AND NOT EXISTS (
              SELECT 1 FROM empleado_sucursal es
              WHERE es.fkEmpleado = e.oid AND es.fkSucursal = e.fkSucursal
          );
        """
    )

    with op.batch_alter_table('empleado', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_empleado_empresa_sucursal'))
        batch_op.drop_index(batch_op.f('ix_empleado_fkSucursal'))
        batch_op.drop_column('fkSucursal')


def downgrade():
    with op.batch_alter_table('empleado', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fkSucursal', mysql.VARCHAR(length=36), nullable=False))
        batch_op.create_index(batch_op.f('ix_empleado_fkSucursal'), ['fkSucursal'], unique=False)
        batch_op.create_index(batch_op.f('ix_empleado_empresa_sucursal'), ['fkEmpresa', 'fkSucursal'], unique=False)
